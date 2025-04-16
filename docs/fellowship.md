# Fellowship & Moderation Implementation Guide

This guide explains the implementation of fellowship groups and content moderation in the 101Guardians application.

## Overview

We've implemented two major new features:

1. **Fellowship Groups**: Private or public prayer groups where users can share and interact with prayers within a specific community.
2. **Content Moderation System**: A comprehensive system to prevent abuse and ensure the platform maintains a safe, supportive environment.

## Fellowship Groups

### Features

- **Private & Public Fellowships**: Users can create either private (join code required) or public (open to anyone) fellowships.
- **Role-Based Permissions**: Fellowship members can have admin, moderator, or member roles with different permissions.
- **Prayer Sharing**: Users can share their prayers with specific fellowship groups.
- **Membership Management**: Admins can invite, remove, and change roles of members.

### Database Structure

Fellowship groups use three main tables:
- `fellowships`: Stores fellowship details
- `fellowship_members`: Tracks membership and roles
- `fellowship_prayers`: Links prayers to fellowships they're shared with

### User Interface

- **Fellowships Page**: A dedicated page to manage and join fellowships
- **Fellowship Dashboard**: View shared prayers and members
- **Settings Panel**: For admins to manage fellowship properties

### Implementation Files

- Backend:
  - `models/fellowship_db.py`: Database methods for fellowships
  - `routes/fellowship_routes.py`: API endpoints for fellowship management
  
- Frontend:
  - `templates/fellowships.html`: Main fellowship management page
  - `static/js/fellowships/fellowship.js`: JavaScript for fellowship UI
  - `static/css/fellowship.css`: Styling for fellowship pages

## Content Moderation

### Features

- **Prayer Reporting**: Users can report inappropriate content
- **Moderation Dashboard**: For admins and moderators to review reports
- **User Management**: Ability to assign roles and manage user status
- **Anti-Abuse Mechanisms**: Rate limiting, reputation system, and content filtering

### Database Structure

Moderation uses several tables:
- `reports`: Tracks user-submitted reports
- User role/status fields added to the `users` table
- Reputation tracking for user trustworthiness

### User Interface

- **Report Buttons**: Added to prayers for users to report content
- **Moderation Dashboard**: For reviewing reports and taking action
- **Admin Controls**: For managing moderators and overall system

### Implementation Files

- Backend:
  - `models/moderation_db.py`: Database methods for moderation
  - `routes/moderation_routes.py`: API endpoints for moderation actions
  
- Frontend:
  - `templates/moderation.html`: Moderation dashboard
  - `static/js/moderation/moderation.js`: JavaScript for moderation UI
  - `static/js/prayers/report.js`: Handling prayer reporting
  - `static/css/moderation.css`: Styling for moderation interface

## Security Measures

The implementation includes several security measures:

1. **Role-Based Access Control**:
   - Only fellowship admins can modify settings and manage members
   - Only site admins/moderators can access moderation features
   - Middleware to verify permissions on all protected routes

2. **Content Protection**:
   - Private fellowships accessible only via join code
   - Prayers shared only with specific fellowships
   - Report system for flagging problematic content

3. **User Protection**:
   - User suspension/banning for repeated violations
   - Reputation system to track trustworthiness
   - Rate limiting on sensitive operations

## How to Use

### For End Users

**Fellowships:**
1. Navigate to the Fellowships page from the main menu
2. Create a new fellowship or join existing ones
3. Share prayers with your fellowships
4. Manage membership and settings if you're an admin

**Reporting Content:**
1. Click the "Report" button on any prayer
2. Select a reason for reporting
3. Add additional details if needed
4. Submit the report for moderator review

### For Administrators

**Moderation:**
1. Access the Moderation Dashboard from the main menu
2. Review reported content and take appropriate action
3. Manage user roles and status as needed
4. Monitor suspicious activity

## Future Enhancements

Potential improvements for future development:

1. **Enhanced Fellowship Features**:
   - Fellowship-specific prayer requests
   - Fellowship events and calendar
   - Fellowship chat/discussion
   - Customizable fellowship themes

2. **Advanced Moderation Tools**:
   - Automated content filtering
   - Machine learning for abuse detection
   - More detailed audit logging
   - Advanced analytics on user behavior

## Setting Up Initial Administrators

To set up the initial administrator for the system, use the following SQL command:

```sql
UPDATE users 
SET role = 'admin' 
WHERE id = '[user_id]';
```

Replace `[user_id]` with the ID of the user who should be the administrator.

## Best Practices

1. **Regular Moderation Review**:
   - Check the moderation dashboard regularly
   - Respond to reports promptly
   - Document actions taken

2. **Fellowship Management**:
   - Encourage users to create meaningful fellowship groups
   - Promote responsible sharing within fellowships
   - Ensure private fellowships rotate join codes periodically

3. **User Communication**:
   - Clearly communicate community guidelines
   - Provide feedback on reported content
   - Explain moderation actions when taken
