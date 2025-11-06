#!/bin/bash

echo "==================================="
echo "Step 1: Getting Tokens"
echo "==================================="
RESPONSE=$(curl -s http://localhost:3000/api/auth/tokens)
echo "$RESPONSE"
echo ""

USER_TOKEN=$(echo $RESPONSE | grep -o '"userToken":"[^"]*' | cut -d'"' -f4)
ADMIN_TOKEN=$(echo $RESPONSE | grep -o '"adminToken":"[^"]*' | cut -d'"' -f4)

echo "User Token: $USER_TOKEN"
echo "Admin Token: $ADMIN_TOKEN"
echo ""

echo "==================================="
echo "Step 2: Test with User Token (Expect 200 OK)"
echo "==================================="
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Authorization: Bearer $USER_TOKEN" \
  http://localhost:3000/api/auth/protected/user-status
echo ""

echo "==================================="
echo "Step 3: Test with Admin Token (Expect 200 OK)"
echo "==================================="
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:3000/api/auth/protected/user-status
echo ""

echo "==================================="
echo "Step 4: Test without Token (Expect 401)"
echo "==================================="
curl -s -w "\nHTTP Status: %{http_code}\n" \
  http://localhost:3000/api/auth/protected/user-status
echo ""

echo "==================================="
echo "Step 5: Test with Invalid Token (Expect 401)"
echo "==================================="
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Authorization: Bearer invalid_token_here" \
  http://localhost:3000/api/auth/protected/user-status
echo ""
