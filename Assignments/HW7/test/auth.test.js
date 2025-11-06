const request = require('supertest');
const app = require('../app');

describe('GET /api/auth/protected/user-status', () => {
  let userToken, adminToken;

  beforeAll(async () => {
    const response = await request(app).get('/api/auth/tokens');
    userToken = response.body.userToken;
    adminToken = response.body.adminToken;
  });

  it('should allow access with a valid standard user token (200 OK)', async () => {
    await request(app)
      .get('/api/auth/protected/user-status')
      .set('Authorization', `Bearer ${userToken}`)
      .expect(200);
  });

  it('should allow access with a valid admin token (200 OK)', async () => {
    await request(app)
      .get('/api/auth/protected/user-status')
      .set('Authorization', `Bearer ${adminToken}`)
      .expect(200);
  });

  it('should deny access with 401 when the token is missing', async () => {
    await request(app)
      .get('/api/auth/protected/user-status')
      .expect(401);
  });
});