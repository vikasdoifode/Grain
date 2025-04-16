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

// Image upload route
app.post("/upload", (req, res) => {
    console.log("🛬 Upload received");

    if (!req.body || req.body.length === 0) {
        return res.status(400).send("No image received");
    }

    const imagePath = path.join(UPLOAD_DIR, `image_${Date.now()}.jpg`);
    fs.writeFileSync(imagePath, req.body);
    console.log("✅ Image saved:", imagePath);

    // Keep only the latest 5 images
    let files = fs.readdirSync(UPLOAD_DIR).map(file => ({
        name: file,
        time: fs.statSync(path.join(UPLOAD_DIR, file)).mtime.getTime()
    }));
    files.sort((a, b) => b.time - a.time);

    while (files.length > 5) {
        let oldestFile = path.join(UPLOAD_DIR, files.pop().name);
        fs.unlinkSync(oldestFile);
    }

    // Optional: run image comparison script
    const pythonProcess = spawn("python", ["compare_images.py", UPLOAD_DIR]);

    pythonProcess.stdout.on("data", (data) => {
        console.log(`🔍 Image Comparison Result: ${data}`);
    });

    pythonProcess.stderr.on("data", (data) => {
        console.error(`❌ Error: ${data}`);
    });

    res.status(200).send("✅ Image received successfully!");
});

// ✅ Serve uploaded images statically
app.use("/uploads", express.static(UPLOAD_DIR));

// ✅ API to list uploaded images
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
    console.log(`🚀 Server running on http://localhost:${PORT}`);
});
