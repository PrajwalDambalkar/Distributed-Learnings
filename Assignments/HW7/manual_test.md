# Manual Verification Steps

## 1. Start the Server

```bash
npm start
# or
node app.js
```

## 2. Test with curl or Postman

### Get Test Tokens

```bash
curl http://localhost:3000/api/auth/tokens
```

This will return:

```json
{
  "userToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "adminToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Test with User Token (Should return 200 OK)

```bash
curl -H "Authorization: Bearer YOUR_USER_TOKEN" \
  http://localhost:3000/api/auth/protected/user-status
```

### Test with Admin Token (Should return 200 OK)

```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  http://localhost:3000/api/auth/protected/user-status
```

### Test without Token (Should return 401)

```bash
curl http://localhost:3000/api/auth/protected/user-status
```

## What You Should See

✅ **With valid token**:

```json
{
  "message": "Access granted",
  "user": { "role": "user" } // or "admin"
}
```

❌ **Without token**:

```json
{
  "error": "Access denied. No token provided."
}
```

❌ **With invalid token**:

```json
{
  "error": "Invalid token."
}
```
