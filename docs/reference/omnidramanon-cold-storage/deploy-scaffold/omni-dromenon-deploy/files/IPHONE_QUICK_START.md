# 📱 iPhone Quick Start

## 🚀 ONE-MINUTE SETUP

### On Your Mac:

```bash
# 1. Navigate to the project
cd ~/Workspace/omni-dromenon-machina

# 2. Make startup script executable
chmod +x START_LOCAL_IPHONE.sh

# 3. Run it
./START_LOCAL_IPHONE.sh
```

Script will:
- ✅ Detect your Mac's local IP
- ✅ Build Docker images (first time only)
- ✅ Start all services
- ✅ Print iPhone URL

### On Your iPhone:

1. **Open Safari**
2. **Enter URL from Mac output**
   - Example: `http://192.168.1.100`
3. **Press Go**
4. **Bookmark it** (top menu → Add Bookmark)

Done! Now you can:
- View the project website
- Test the API
- See real-time performance
- Share link with collaborators

---

## 📋 What's Running

When you see "Docker services running", you have:

| Service | URL | Purpose |
|---------|-----|---------|
| Website | `http://IP` | Landing page + showcase |
| API | `http://IP:3000` | Core Engine API |
| Frontend | `http://IP:3001` | Performance interface |
| Redis | `localhost:6379` | Cache (internal) |

---

## 🎯 Typical Workflow

### Start Services (on Mac)
```bash
cd ~/Workspace/omni-dromenon-machina
./START_LOCAL_IPHONE.sh
```

### View on iPhone
```
Open Safari → Visit http://YOUR-IP
```

### Stop Services
```
Press Ctrl+C in Terminal
```

### View Logs (another Terminal)
```bash
cd ~/Workspace/omni-dromenon-machina
docker-compose logs -f
```

---

## 🆘 Troubleshooting

### "Can't connect from iPhone"
1. ✅ iPhone is on same WiFi as Mac?
2. ✅ Mac IP correct? (Check Terminal output)
3. ✅ Firewall blocking port 80?
   - System Preferences → Security & Privacy → Firewall Options
   - Add Docker to allowed apps

### "Get IP address on Mac"
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# Look for: 192.168.x.x or 10.x.x.x
```

### "Services won't start"
```bash
# Kill any old containers
docker-compose down -v

# Restart
./START_LOCAL_IPHONE.sh
```

### "Can't connect to API from website"
- iPhone: Make sure using IP address, not localhost
- Example: `http://192.168.1.100` (not `http://localhost`)

---

## 📡 Network Tips

### Get Better IP Display
Edit `START_LOCAL_IPHONE.sh` to print QR code:
```bash
# Install qrencode: brew install qrencode
echo "$LOCAL_IP" | qrencode -t ANSIUTF8
```

### Share with Collaborators
```bash
"Visit http://192.168.1.100 on WiFi with password: [your-wifi-password]" # allow-secret
```

### Test from Different Device
```bash
# From iPhone/iPad on same WiFi:
curl http://YOUR-MAC-IP/health
```

---

## ⚡ Pro Tips

### Keep Terminal Open
Leave Terminal with `START_LOCAL_IPHONE.sh` running. Close it to stop services.

### Monitor Logs
Open second Terminal:
```bash
cd ~/Workspace/omni-dromenon-machina
docker-compose logs -f core-engine
```

### Test API from iPhone
1. Open Safari
2. Visit: `http://YOUR-IP:3000/health`
3. Should see: `{"status":"healthy"}`

### Bookmark for Easy Access
1. Safari → Visit URL
2. Share button → Add Bookmark
3. Name: "Omni-Dromenon"
4. Location: "Favorites"

---

**That's it! You're now running Omni-Dromenon-Machina locally with iPhone access.** 🚀
