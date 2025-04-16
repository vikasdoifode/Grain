const express = require("express");
const fs = require("fs");
const path = require("path");
const bodyParser = require("body-parser");
const { spawn } = require("child_process");

const app = express();
const PORT = process.env.PORT || 3000;
const UPLOAD_DIR = path.join(__dirname, "uploads");

// Ensure upload directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

app.use(bodyParser.raw({ type: "image/jpeg", limit: "10mb" }));

// POST /upload - Uploads image and keeps only latest 5
app.post("/upload", (req, res) => {
    console.log("🛬 Upload received");

    if (!req.body || req.body.length === 0) {
        return res.status(400).send("No image received");
    }

    const filename = `image_${Date.now()}.jpg`;
    const imagePath = path.join(UPLOAD_DIR, filename);

    fs.writeFileSync(imagePath, req.body);
    console.log("✅ Image saved:", filename);

    // 🧹 Keep only the latest 5 images
    const files = fs.readdirSync(UPLOAD_DIR)
        .filter(file => /\.(jpg|jpeg|png)$/i.test(file))
        .map(file => ({
            name: file,
            time: fs.statSync(path.join(UPLOAD_DIR, file)).mtime.getTime()
        }))
        .sort((a, b) => b.time - a.time); // Newest first

    if (files.length > 5) {
        const toDelete = files.slice(5); // Files beyond the 5 newest
        toDelete.forEach(file => {
            const fullPath = path.join(UPLOAD_DIR, file.name);
            fs.unlinkSync(fullPath);
            console.log(`🗑️ Deleted old image: ${file.name}`);
        });
    }

    // Optional: run Python comparison script
    const pythonProcess = spawn("python", ["compare_images.py", UPLOAD_DIR]);

    pythonProcess.stdout.on("data", (data) => {
        console.log(`🔍 Comparison Output: ${data}`);
    });

    pythonProcess.stderr.on("data", (data) => {
        console.error(`❌ Python Error: ${data}`);
    });

    res.status(200).send("✅ Image received successfully!");
});

// Serve uploaded images statically
app.use("/uploads", express.static(UPLOAD_DIR));

// GET /api/images - Returns list of image URLs (newest first)
app.get("/api/images", (req, res) => {
    fs.readdir(UPLOAD_DIR, (err, files) => {
        if (err) {
            console.error("❌ Failed to list images:", err);
            return res.status(500).json({ error: "Failed to list images" });
        }

        const sortedFiles = files
            .filter(file => /\.(jpg|jpeg|png)$/i.test(file))
            .map(file => ({
                name: file,
                time: fs.statSync(path.join(UPLOAD_DIR, file)).mtime.getTime()
            }))
            .sort((a, b) => b.time - a.time)
            .map(f => f.name);

        const baseUrl = req.protocol + "://" + req.get("host");
        const imageUrls = sortedFiles.map(file => `${baseUrl}/uploads/${file}`);

        res.json(imageUrls);
    });
});

app.listen(PORT, () => {
    console.log(`🚀 Server running at http://localhost:${PORT}`);
});
