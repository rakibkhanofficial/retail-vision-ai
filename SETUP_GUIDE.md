# 🚀 Setup & Deployment Guide - Retail Vision AI

## 📋 Prerequisites

### Required
- **Docker Desktop** (latest version)
  - Download: https://www.docker.com/products/docker-desktop
  - Minimum 8GB RAM allocated to Docker
  - 20GB free disk space

- **Gemini API Key** (free tier available)
  - Get it from: https://makersuite.google.com/app/apikey
  - No credit card required for free tier
  - Generous quota for testing

### Optional
- **Git** for version control
- **VS Code** or preferred IDE
- **Postman** for API testing

## ⚡ Quick Start (5 Minutes)

### Step 1: Get Your API Key

1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### Step 2: Setup Environment

```bash
cd retail-vision-ai

# Create environment file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor

# Add your Gemini API key:
GEMINI_API_KEY=AIzaSyC8FpK4...your-actual-key

# Generate secure secrets (or use provided defaults for testing):
SECRET_KEY=your-random-32-char-string-here
NEXTAUTH_SECRET=another-random-32-char-string
```

**Generating Secure Keys:**
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### Step 3: Build and Run

```bash
# Build and start all services
docker compose up --build

# Or run in background:
docker compose up -d --build
```

**First build takes 5-10 minutes** (downloads models and dependencies)

**Wait for:**
```
backend-1   | 🚀 Retail Vision AI v1.0.0 starting up...
backend-1   | INFO: Application startup complete.
frontend-1  | ✓ Ready in 2.1s
```

### Step 4: Access Application

Open your browser and navigate to:

**http://localhost:3000**

## 📱 First Use

### 1. Create Account

1. Click "Get Started" on landing page
2. Fill in registration form:
   - Email: your@email.com
   - Username: yourusername
   - Full Name: Your Name
   - Password: (minimum 6 characters)
3. Click "Sign Up"
4. Automatically logged in

### 2. Upload First Image

**Option A: Camera Capture**
1. Click camera icon in upload area
2. Allow camera access when prompted
3. Position camera at refrigerator/cooler
4. Click "Capture" button
5. Review photo, click "Use This Photo"

**Option B: Drag & Drop**
1. Drag image file into upload area
2. See preview instantly
3. Click "Detect Products"

**Option C: File Browse**
1. Click anywhere in upload area
2. Select image from device
3. Click "Open"

### 3. View Results

Results appear in ~3-5 seconds:

**Visual Analysis:**
- Annotated image with bounding boxes
- Color-coded object classes
- Confidence scores

**Data Table:**
- All detected objects listed
- Click column headers to sort
- View coordinates and metrics

**Retail Insights:**
- Brand detection results
- Shelf organization (rows/columns)
- Product positioning details
- Stock level assessment
- Restocking recommendations

### 4. Ask Questions

Scroll to Q&A section and ask:
- "How many products are on the top shelf?"
- "Which brands are detected?"
- "What's the stock level?"
- "Any empty spaces?"

## 🔧 Advanced Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# Application
APP_NAME=Retail Vision AI
DEBUG=False  # Set to True for development

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days

# YOLO Settings
CONFIDENCE_THRESHOLD=0.25  # Lower = more sensitive (0.1-0.9)
IOU_THRESHOLD=0.45         # Overlap threshold (0.1-0.9)

# File Upload
MAX_FILE_SIZE=10485760     # 10MB in bytes
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.webp
```

### Frontend Configuration

Edit `frontend/.env.local`:

```bash
# API Connection
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

# Optional Features
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_PWA=false
```

## 🐳 Docker Commands

### Basic Operations

```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Stop services (keep data)
docker compose down

# Stop and remove all data
docker compose down -v

# Restart specific service
docker compose restart backend
docker compose restart frontend

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### Troubleshooting

```bash
# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up

# Check service status
docker compose ps

# Enter container shell
docker compose exec backend /bin/bash
docker compose exec frontend /bin/sh

# Check resource usage
docker stats
```

## 🌐 Production Deployment

### Option 1: VPS Deployment (DigitalOcean, Linode, etc.)

**Requirements:**
- Ubuntu 22.04 LTS
- 4GB RAM minimum
- 40GB disk space
- Docker and Docker Compose installed

**Steps:**

1. **Server Setup**
```bash
# SSH into your server
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

2. **Clone and Configure**
```bash
# Clone your repository
git clone your-repo-url
cd retail-vision-ai

# Setup environment
cp .env.example .env
nano .env  # Add your keys

# Update docker-compose for production
nano docker-compose.yml
# Change:
# - NEXTAUTH_URL=https://yourdomain.com
# - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

3. **Setup Nginx Reverse Proxy**
```bash
# Install Nginx
sudo apt-get install nginx certbot python3-certbot-nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/retail-vision
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/retail-vision /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

4. **Start Application**
```bash
docker compose up -d
```

### Option 2: Cloud Platform Deployment

**AWS (Elastic Beanstalk + RDS):**
- Use Multi-container Docker configuration
- RDS for PostgreSQL database
- S3 for image storage
- CloudFront for CDN

**GCP (Cloud Run + Cloud SQL):**
- Separate frontend and backend to Cloud Run
- Cloud SQL for PostgreSQL
- Cloud Storage for images
- Cloud CDN

**Azure (Container Instances + PostgreSQL):**
- Azure Container Instances for services
- Azure Database for PostgreSQL
- Azure Blob Storage for images
- Azure CDN

### Option 3: Managed Kubernetes (Production Scale)

```yaml
# k8s-deployment.yaml example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retail-vision-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/retail-vision-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 🔒 Security Hardening

### Production Checklist

- [ ] Change all default secrets
- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS (SSL certificate)
- [ ] Configure firewall (UFW or cloud security groups)
- [ ] Set up rate limiting
- [ ] Enable CORS for specific domains only
- [ ] Regular security updates
- [ ] Database backups automated
- [ ] Use environment variables (never commit secrets)
- [ ] Enable logging and monitoring
- [ ] Set up alerts for errors
- [ ] Implement API rate limiting
- [ ] Use CDN for static assets
- [ ] Enable gzip compression

### Environment Variables Security

```bash
# Use a secrets manager in production:
# - AWS Secrets Manager
# - Google Secret Manager
# - Azure Key Vault
# - HashiCorp Vault

# Example AWS Secrets Manager:
aws secretsmanager create-secret \
    --name retail-vision/gemini-key \
    --secret-string "your-api-key"

# Retrieve in application:
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='retail-vision/gemini-key')
```

## 📊 Monitoring

### Application Monitoring

**Logging:**
```bash
# View application logs
docker compose logs -f backend | grep ERROR
docker compose logs -f frontend | grep ERROR

# Save logs to file
docker compose logs > logs.txt
```

**Health Checks:**
```bash
# Backend health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "database": "operational",
#     "yolo": "operational",
#     "gemini": "operational"
#   }
# }
```

**Performance Monitoring:**
- Use Prometheus + Grafana
- New Relic
- Datadog
- AWS CloudWatch

### Database Monitoring

```bash
# Connect to database
docker compose exec db psql -U postgres -d retail_vision

# Check table sizes
SELECT 
  schemaname, 
  tablename, 
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check connections
SELECT * FROM pg_stat_activity;
```

## 🔄 Backup & Restore

### Database Backup

```bash
# Create backup
docker compose exec db pg_dump -U postgres retail_vision > backup.sql

# Automated daily backups (cron job)
0 2 * * * cd /path/to/project && docker compose exec -T db pg_dump -U postgres retail_vision | gzip > backups/backup-$(date +\%Y\%m\%d).sql.gz
```

### Restore Database

```bash
# Restore from backup
docker compose exec -T db psql -U postgres retail_vision < backup.sql
```

### Image Backups

```bash
# Sync to S3 (example)
aws s3 sync backend/uploads s3://your-bucket/uploads/

# Sync to cloud storage (rsync)
rsync -avz backend/uploads/ user@backup-server:/backups/uploads/
```

## 🧪 Testing

### API Testing with curl

```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"test123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=testuser" \
  -F "password=test123"

# Upload image (with token)
curl -X POST http://localhost:8000/api/v1/detections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test-image.jpg" \
  -F "name=Test Detection"
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoints
ab -n 1000 -c 10 http://localhost:8000/health

# Test with authentication
ab -n 100 -c 5 -H "Authorization: Bearer TOKEN" http://localhost:8000/api/v1/detections
```

## 💡 Tips & Best Practices

### Image Quality
- Use clear, well-lit photos
- Minimum resolution: 640x480
- Maximum recommended: 1920x1080
- Avoid blurry or dark images
- Straight-on angle works best

### Retail Photography
- Position camera parallel to shelf
- Include entire product display
- Avoid glare from refrigerator lighting
- Capture at eye level when possible
- Multiple angles for complex displays

### Performance
- Compress images before upload (if >2MB)
- Use thumbnail view for history
- Clear old detections periodically
- Monitor disk space usage
- Adjust YOLO confidence threshold

### Accuracy
- Train custom model for specific brands
- Fine-tune confidence threshold
- Use consistent lighting conditions
- Standardize camera angles
- Validate results manually initially

## 🐛 Common Issues & Solutions

### Issue: Camera Not Working

**Symptoms:**
- Camera permission denied
- Black screen
- "Camera not found"

**Solutions:**
1. Check browser permissions (allow camera access)
2. Use HTTPS (camera requires secure context)
3. Try different browser (Chrome, Firefox, Safari)
4. Check camera not used by another app
5. Restart browser
6. On mobile: check app permissions in settings

### Issue: Slow Detection

**Symptoms:**
- Detection takes >10 seconds
- Application freezes
- Timeout errors

**Solutions:**
1. Reduce image size (<2MB)
2. Increase Docker memory:
   ```bash
   # Docker Desktop -> Settings -> Resources
   # Set RAM to 8GB+
   ```
3. Close other applications
4. Check CPU usage: `docker stats`
5. Use lighter YOLO model (already using yolov8n)

### Issue: No Analysis Results

**Symptoms:**
- Detection completes but no retail analysis
- "Analysis not available"
- Blank insights section

**Solutions:**
1. Verify Gemini API key in backend/.env
2. Check API quota: https://makersuite.google.com
3. Check backend logs: `docker compose logs backend`
4. Restart backend: `docker compose restart backend`
5. Test with different image

### Issue: Login Not Working

**Symptoms:**
- "Invalid credentials" on correct password
- Session expires immediately
- Redirects to login after auth

**Solutions:**
1. Check NEXTAUTH_SECRET is set
2. Verify SECRET_KEY matches backend
3. Clear browser cookies
4. Check database connection
5. Restart services: `docker compose restart`

### Issue: Port Already in Use

**Symptoms:**
- "Port 3000 is already allocated"
- "Port 8000 is already allocated"

**Solutions:**
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 PID

# Or change ports in docker-compose.yml:
ports:
  - "3001:3000"  # frontend
  - "8001:8000"  # backend
```

## 📞 Getting Help

### Documentation
- Main README.md
- API docs: http://localhost:8000/docs
- Project structure: PROJECT_STRUCTURE.md

### Community Support
- GitHub Issues
- Stack Overflow (tag: retail-vision-ai)
- Discord (if available)

### Professional Support
- Email: support@yourcompany.com
- Consulting: Schedule a call
- Custom Development: Contact us

## 🎓 Next Steps

After successful setup:

1. **Customize for Your Needs**
   - Add your logo to landing page
   - Customize color scheme
   - Add specific product categories
   - Train custom YOLO model

2. **Integrate with Systems**
   - Connect to inventory management
   - Export to Excel/CSV
   - API webhooks for automation
   - Mobile app development

3. **Scale for Production**
   - Set up monitoring
   - Configure backups
   - Enable HTTPS
   - Deploy to cloud

4. **Train Your Team**
   - Create user guides
   - Record video tutorials
   - Conduct training sessions
   - Establish best practices

---

**Need more help?** Refer to README.md for detailed feature documentation.

**Ready to deploy?** Follow the production deployment section above.

**Want to customize?** Check PROJECT_STRUCTURE.md for code organization.
