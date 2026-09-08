const express = require('express');
const session = require('express-session');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = express();
const db = new sqlite3.Database('./db.sqlite');

/*
FLAG in /fla4444444aaaaaagg.txt
*/

app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(
  session({
    secret: 'welcometoycb2025',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false },
  }),
);

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

const checkPermission = (req, res, next) => {
  if (req.path === '/login' || req.path === '/register') return next();
  if (!req.session.user) return res.redirect('/login');
  if (!req.session.user.isAdmin) return res.status(403).send('无权限访问');
  next();
};

app.use(checkPermission);

app.get('/', (req, res) => {
  fs.readdir(path.join(__dirname, 'documents'), (err, files) => {
    if (err) {
      console.error('读取目录时发生错误:', err);
      return res.status(500).send('目录读取失败');
    }
    req.session.files = files;
    res.render('files', { files, user: req.session.user });
  });
});

app.get('/login', (req, res) => {
  res.render('login');
});

app.get('/register', (req, res) => {
  res.render('register');
});

app.get('/upload', (req, res) => {
  if (!req.session.user) return res.redirect('/login');
  res.render('upload', { user: req.session.user });
  //todoing
});

app.get('/logout', (req, res) => {
  req.session.destroy(err => {
    if (err) {
      console.error('退出时发生错误:', err);
      return res.status(500).send('退出失败');
    }
    res.redirect('/login');
  });
});

app.post('/login', async (req, res) => {
  const username = req.body.username;
  const password = req.body.password;
  const sql = `SELECT * FROM users WHERE (username = "${username}") AND password = ("${password}")`;
  db.get(sql, async (err, user) => {
    if (!user) {
      return res.status(401).send('账号密码出错！！');
    }
    req.session.user = {
      id: user.id,
      username: user.username,
      isAdmin: user.is_admin,
    };
    res.redirect('/');
  });
});

app.post('/register', (req, res) => {
  const { username, password, confirmPassword } = req.body;

  if (password !== confirmPassword) {
    return res.status(400).send('两次输入的密码不一致');
  }

  db.exec(
    `INSERT INTO users (username, password) VALUES ('${username}', '${password}')`,
    function (err) {
      if (err) {
        console.error('注册失败:', err);
        return res.status(500).send('注册失败，用户名可能已存在');
      }
      res.redirect('/login');
    },
  );
});

app.get('/download', (req, res) => {
  if (!req.session.user) return res.redirect('/login');
  const filename = req.query.filename;
  if (filename.startsWith('/') || filename.startsWith('./')) {
    return res.status(400).send('WAF');
  }
  if (
    filename.includes('../../') ||
    filename.includes('.././') ||
    filename.includes('f') ||
    filename.includes('//')
  ) {
    return res.status(400).send('WAF');
  }
  if (!filename || path.isAbsolute(filename)) {
    return res.status(400).send('无效文件名');
  }
  const filePath = path.join(__dirname, 'documents', filename);
  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).send('文件不存在');
  }
});

const PORT = 80;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
