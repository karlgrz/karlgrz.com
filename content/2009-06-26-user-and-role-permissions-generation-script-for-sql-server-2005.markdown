author: karlgrz 
comments: true
date: 2009-06-26 15:48:00
slug: user-and-role-permissions-generation-script-for-sql-server-2005
title: User and Role Permissions Generation script for SQL Server 2005
category: Coding
tags: sql, sqlserver, tsql

I've come across many instances in the past where I have needed to duplicate permissions for a single user or role on SQL Server 2005 (usually when trying to version control permissions for a department or group of users, for example). This was a tedious task that I used to dread when I first started commanding more of the DBA responsibilities.  
  
I've been using a couple of scripts to help myself with these tasks, and thought I would share them.  
  
Enjoy!  
  
``` sql ScriptUserPermissions    
    
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
/*
==========================================================================
Procedure Name:  ScriptUserPermissions
Author:          Karl Grzeszczak

Purpose:    Generate all permissions attached to a particular user for the database it is run in.
            NOTE: This stored procedure can be run in ANY database.

Inputs:     @userName  varchar(200)  Name of the user.

Outputs:    .sql script to generate user's permissions.

==========================================================================  
*/
CREATE PROCEDURE [dbo].[ScriptUserPermissions]
(
  @userName varchar(200)
)
AS
BEGIN
  DECLARE @DatabaseUserName [sysname]
  SET @DatabaseUserName = @userName

  SET NOCOUNT ON

  DECLARE
    @errStatement [varchar](8000),
    @msgStatement [varchar](8000),
    @DatabaseUserID [smallint],
    @ServerUserName [sysname],
    @RoleName [varchar](8000),
    @ObjectID [int],
    @ObjectName [varchar](261)

  SELECT
    @DatabaseUserID = [sysusers].[uid],
    @ServerUserName = [master].[dbo].[syslogins].[loginname]
  FROM 
    [dbo].[sysusers]
      INNER JOIN [master].[dbo].[syslogins]
      ON [sysusers].[sid] = [master].[dbo].[syslogins].[sid]
  WHERE 
    [sysusers].[name] = @DatabaseUserName

  IF @DatabaseUserID IS NULL
  BEGIN
    SET @errStatement = 'User ' + @DatabaseUserName + ' does not exist in ' + DB_NAME() + CHAR(13) +
                  'Please provide the name of a current user in ' + DB_NAME() + ' you wish to script.'
    RAISERROR(@errStatement, 16, 1)
  END
  ELSE
  BEGIN
    SET @msgStatement = '--Security creation script for user ' + @ServerUserName + CHAR(13) +
                  '--Created At: ' + CONVERT(varchar, GETDATE(), 112) + REPLACE(CONVERT(varchar, GETDATE(), 108), ':', '') + CHAR(13) +
                  '--Created By: ' + SUSER_NAME() + CHAR(13) +
                  '--Add User To Database' + CHAR(13) +                  
                  'EXEC [sp_grantdbaccess]' + CHAR(13) +
                  CHAR(9) + '@loginame = ''' + @ServerUserName + ''',' + CHAR(13) +
                  CHAR(9) + '@name_in_db = ''' + @DatabaseUserName + '''' + CHAR(13) +
                  '--Add User To Roles'
    PRINT @msgStatement
    DECLARE _sysusers
    CURSOR
    LOCAL
    FORWARD_ONLY
    READ_ONLY
    FOR
    SELECT
    [name]
    FROM [dbo].[sysusers]
    WHERE
    [uid] IN
    (
    SELECT
    [groupuid]
    FROM [dbo].[sysmembers]
    WHERE [memberuid] = @DatabaseUserID
    )
    OPEN _sysusers
    FETCH
    NEXT
    FROM _sysusers
    INTO @RoleName
    WHILE @@FETCH_STATUS = 0
    BEGIN
      SET @msgStatement = 'EXEC [sp_addrolemember]' + CHAR(13) +
                    CHAR(9) + '@rolename = ''' + @RoleName + ''',' + CHAR(13) +
                    CHAR(9) + '@membername = ''' + @DatabaseUserName + ''''
      PRINT @msgStatement
      FETCH
      NEXT
      FROM _sysusers
      INTO @RoleName
    END

  SET @msgStatement = '--Set Object Specific Permissions'
  PRINT @msgStatement
  
  DECLARE _sysobjects
  CURSOR
  LOCAL
  FORWARD_ONLY
  READ_ONLY
  FOR
  SELECT
  DISTINCT([sysobjects].[id]),
  '[' + USER_NAME([sysobjects].[uid]) + '].[' + [sysobjects].[name] + ']'
  FROM [dbo].[sysprotects]
  INNER JOIN [dbo].[sysobjects]
  ON [sysprotects].[id] = [sysobjects].[id]
  WHERE [sysprotects].[uid] = @DatabaseUserID
  OPEN _sysobjects
  FETCH
  NEXT
  FROM _sysobjects
  INTO
  @ObjectID,
  @ObjectName
  WHILE @@FETCH_STATUS = 0
  BEGIN
    SET @msgStatement = ''
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 193 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'SELECT,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 195 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'INSERT,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 197 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'UPDATE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 196 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'DELETE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 224 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'EXECUTE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 26 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'REFERENCES,'
    IF LEN(@msgStatement) > 0
    BEGIN
      IF RIGHT(@msgStatement, 1) = ','
        SET @msgStatement = LEFT(@msgStatement, LEN(@msgStatement) - 1)
        SET @msgStatement = 'GRANT' + CHAR(13) +
                      CHAR(9) + @msgStatement + CHAR(13) +
                      CHAR(9) + 'ON ' + @ObjectName + CHAR(13) +
                      CHAR(9) + 'TO ' + @DatabaseUserName
        PRINT @msgStatement
    END
    SET @msgStatement = ''
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 193 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'SELECT,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 195 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'INSERT,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 197 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'UPDATE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 196 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'DELETE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 224 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'EXECUTE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseUserID AND [action] = 26 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'REFERENCES,'
    IF LEN(@msgStatement) > 0
    BEGIN
      IF RIGHT(@msgStatement, 1) = ','
      SET @msgStatement = LEFT(@msgStatement, LEN(@msgStatement) - 1)
      SET @msgStatement = 'DENY' + CHAR(13) +
                    CHAR(9) + @msgStatement + CHAR(13) +
                    CHAR(9) + 'ON ' + @ObjectName + CHAR(13) +
                    CHAR(9) + 'TO ' + @DatabaseUserName
      PRINT @msgStatement
    END
    FETCH
    NEXT
    FROM _sysobjects
    INTO
    @ObjectID,
    @ObjectName
  END
  CLOSE _sysobjects
  DEALLOCATE _sysobjects
  END
END

```
  
  
``` sql ScriptRolePermissions    
    
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
/*
==========================================================================
Procedure Name:  ScriptRolePermissions
Author:          Karl Grzeszczak

Purpose:    Generate all permissions attached to a particular role for the database it is run in.
            NOTE: This stored procedure can be run in ANY database.

Inputs:    @roleName  varchar(200)  Name of the role.

Outputs:    .sql script to generate role's permissions.

==========================================================================  
*/
CREATE PROCEDURE [dbo].[ScriptRolePermissions]
(
  @roleName varchar(200)
)
AS
BEGIN
  DECLARE @DatabaseRoleName [sysname]
  SET @DatabaseRoleName = @roleName

  SET NOCOUNT ON
  DECLARE
    @errStatement [varchar](8000),
    @msgStatement [varchar](8000),
    @DatabaseRoleID [smallint],
    @IsApplicationRole [bit],
    @ObjectID [int],
    @ObjectName [sysname]

  SELECT
    @DatabaseRoleID = [uid],
    @IsApplicationRole = CAST([isapprole] AS bit)
  FROM 
    [dbo].[sysusers]
  WHERE
    [name] = @DatabaseRoleName AND
    (
      [issqlrole] = 1 OR [isapprole] = 1
    ) AND 
    [name] NOT IN
    (
      'public',
      'INFORMATION_SCHEMA',
      'db_owner',
      'db_accessadmin',
      'db_securityadmin',
      'db_ddladmin',
      'db_backupoperator',
      'db_datareader',
      'db_datawriter',
      'db_denydatareader',
      'db_denydatawriter'
    )

  IF @DatabaseRoleID IS NULL
  BEGIN
    IF @DatabaseRoleName IN
    (
      'public',
      'INFORMATION_SCHEMA',
      'db_owner',
      'db_accessadmin',
      'db_securityadmin',
      'db_ddladmin',
      'db_backupoperator',
      'db_datareader',
      'db_datawriter',
      'db_denydatareader',
      'db_denydatawriter'
    )
    SET @errStatement = 'Role ' + @DatabaseRoleName + ' is a fixed database role and cannot be scripted.'
    ELSE
    SET @errStatement = 'Role ' + @DatabaseRoleName + ' does not exist in ' + DB_NAME() + '.' + CHAR(13) +
                  'Please provide the name of a current role in ' + DB_NAME() + ' you wish to script.'
    RAISERROR(@errStatement, 16, 1)
  END
  ELSE
  BEGIN
    SET @msgStatement = '--Security creation script for role ' + @DatabaseRoleName + CHAR(13) +
                  '--Created At: ' + CONVERT(varchar, GETDATE(), 112) + REPLACE(CONVERT(varchar, GETDATE(), 108), ':', '') + CHAR(13) +
                  '--Created By: ' + SUSER_NAME() + CHAR(13) +
                  '--Add Role To Database' + CHAR(13)
    IF @IsApplicationRole = 1
    SET @msgStatement = @msgStatement + 'EXEC sp_addapprole' + CHAR(13) +
                  CHAR(9) + '@rolename = ''' + @DatabaseRoleName + '''' + CHAR(13) +
                  CHAR(9) + '@password = ''{Please provide the password here}''' + CHAR(13)
    ELSE
    BEGIN
      SET @msgStatement = @msgStatement + 'EXEC sp_addrole' + CHAR(13) +
                    CHAR(9) + '@rolename ''' + @DatabaseRoleName + '''' + CHAR(13)
    END
    SET @msgStatement = @msgStatement + '--Set Object Specific Permissions For Role'
    PRINT @msgStatement
    DECLARE _sysobjects
    CURSOR
    LOCAL
    FORWARD_ONLY
    READ_ONLY
    FOR
    SELECT
    DISTINCT([sysobjects].[id]),
    '[' + USER_NAME([sysobjects].[uid]) + '].[' + [sysobjects].[name] + ']'
    FROM [dbo].[sysprotects]
    INNER JOIN [dbo].[sysobjects]
    ON [sysprotects].[id] = [sysobjects].[id]
    WHERE [sysprotects].[uid] = @DatabaseRoleID
    OPEN _sysobjects
    FETCH
    NEXT
    FROM _sysobjects
    INTO
    @ObjectID,
    @ObjectName
  
    WHILE @@FETCH_STATUS = 0
    BEGIN
    SET @msgStatement = ''
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 193 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'SELECT,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 195 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'INSERT,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 197 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'UPDATE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 196 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'DELETE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 224 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'EXECUTE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 26 AND [protecttype] = 205)
    SET @msgStatement = @msgStatement + 'REFERENCES,'
    IF LEN(@msgStatement) > 0
    BEGIN
      IF RIGHT(@msgStatement, 1) = ','
        SET @msgStatement = LEFT(@msgStatement, LEN(@msgStatement) - 1)
      SET @msgStatement = 'GRANT' + CHAR(13) +
                    CHAR(9) + @msgStatement + CHAR(13) +
                    CHAR(9) + 'ON ' + @ObjectName + CHAR(13) +
                    CHAR(9) + 'TO ' + @DatabaseRoleName
      PRINT @msgStatement
    END
    SET @msgStatement = ''
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 193 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'SELECT,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 195 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'INSERT,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 197 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'UPDATE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 196 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'DELETE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 224 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'EXECUTE,'
    IF EXISTS(SELECT * FROM [dbo].[sysprotects] WHERE [id] = @ObjectID AND [uid] = @DatabaseRoleID AND [action] = 26 AND [protecttype] = 206)
    SET @msgStatement = @msgStatement + 'REFERENCES,'
    IF LEN(@msgStatement) > 0
    BEGIN
      IF RIGHT(@msgStatement, 1) = ','
        SET @msgStatement = LEFT(@msgStatement, LEN(@msgStatement) - 1)
      SET @msgStatement = 'DENY' + CHAR(13) +
                    CHAR(9) + @msgStatement + CHAR(13) +
                    CHAR(9) + 'ON ' + @ObjectName + CHAR(13) +
                    CHAR(9) + 'TO ' + @DatabaseRoleName
      PRINT @msgStatement
    END
    FETCH
    NEXT
    FROM _sysobjects
    INTO
    @ObjectID,
    @ObjectName
    END
    CLOSE _sysobjects
    DEALLOCATE _sysobjects
  END 
END

```
