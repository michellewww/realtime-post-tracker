# Email App Setup Instructions 

Dear Professor Yarowsky,

To enable email functionality, our app uses individual Google Cloud credentials. Two essential files — `credentials.json` and `token.json` — are located in the `backend/` folder. These files are required to run the app locally. 
Please kindly prevent other person from accessing our credentials.json or token.json. 

## 📦 Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate (Mac)
   .\env\Scripts\activate (Windows)
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python main.py
   ```

## 🌐 Frontend Setup (Open a New Terminal)

1. Install frontend dependencies:
   ```bash
   npm install
   ```

2. Start the frontend server:
   ```bash
   npm start
   ```
3. The browser should automatically open to our app, but if not, visit
   http://0.0.0.0:8000 instead. 
## 🛠 Troubleshooting

If you encounter a permissions error like:
```
npm ERR! code EACCES
npm ERR! syscall open
```

Fix it with:
```bash
sudo chown -R $(whoami) ~/.npm
```

Then re-run:
```bash
npm install
npm start
```


