Perfect 👍
Below is the **UPDATED, FINAL Copilot prompt** with your **new requirement added** (separate `Frontend` folder), **merged cleanly with the previous instructions**.
You can **directly paste this into GitHub Copilot Chat**.

---

## ✅ **GitHub Copilot Prompt – Frontend Application**

> **Role**: You are a Senior Front-End Developer
> **Tech Stack**: React.js (Vite preferred), HTML5, CSS3, JavaScript
> **Styling**: Tailwind CSS or Bootstrap (choose one)
> **Icons**: React Icons / Font Awesome / Material Icons
> **Backend**: Already implemented separately (ingestion & retrieval APIs for dynamic question paper generation)

---

## 📌 **Project Context**

The backend code exists in a separate repository and is responsible for:

* Content ingestion
* Question retrieval
* Generating a **new question paper every time the user clicks a button**

Your task is to **create ONLY the frontend**, fully separated from backend logic.

---

## 📁 **Folder Structure Requirement (MANDATORY)**

Create a **top-level folder named `Frontend`** inside the project root and place **all frontend-related code inside it**.

### Expected Structure:

```
Frontend/
 ├── public/
 ├── src/
 │   ├── assets/
 │   ├── components/
 │   │   ├── Navbar.jsx
 │   │   ├── Footer.jsx
 │   │   ├── RoleCard.jsx
 │   ├── pages/
 │   │   ├── Home.jsx
 │   │   ├── About.jsx
 │   │   ├── Contact.jsx
 │   │   ├── SignIn.jsx
 │   │   ├── Student.jsx
 │   │   ├── Teacher.jsx
 │   │   ├── Admin.jsx
 │   ├── services/
 │   │   └── api.js   // placeholder for backend calls
 │   ├── App.jsx
 │   └── main.jsx
 ├── index.html
 ├── package.json
 └── README.md
```

---

## 🧭 **Application Pages & Features**

### 1️⃣ Navigation Bar (Global)

Include a responsive **header/navbar** with:

* Application name/logo
* Home
* About
* Contact Us
* Sign In
* Mobile-friendly hamburger menu

---

### 2️⃣ Homepage (`Home.jsx`)

The homepage must display **three role-based frames/cards**, aligned horizontally and responsive.

Each card must include:

* Appropriate icon
* Role title
* Short description
* Hover effect
* Click handler (navigation-ready)

#### 🔹 Role Cards:

1. **Student**

   * Icon: 🎓 (Graduation cap)
   * Description: Generate and practice question papers

2. **Teacher**

   * Icon: 👩‍🏫 (Teacher / board)
   * Description: Create and review question papers

3. **Admin**

   * Icon: 🛠️ (Settings / shield)
   * Description: Manage users and system configuration

---

### 3️⃣ Student Page

* Button: **“Generate Question Paper”**
* On click:

  * Call a placeholder API function
  * Show loading indicator
  * Display generated questions (mock data for now)

---

### 4️⃣ Teacher Page

* UI for:

  * Viewing generated papers
  * Reviewing questions
* Backend integration placeholder only

---

### 5️⃣ Admin Page

* Dashboard-style layout
* Placeholder UI for:

  * User management
  * System settings

---

### 6️⃣ About Page

* Explain:

  * Purpose of the platform
  * AI-based dynamic question generation
  * Benefits for students & teachers

---

### 7️⃣ Contact Us Page

* Contact form:

  * Name
  * Email
  * Message
* Submit button (no backend required)

---

### 8️⃣ Sign In Page

* Basic UI:

  * Email
  * Password
  * Role selection (Student / Teacher / Admin)
* No authentication logic needed (UI only)

---

## 🎨 **UI / UX Guidelines**

* Clean, modern design
* Responsive (mobile + desktop)
* Card-based layout
* Smooth hover animations
* Reusable components
* Consistent color theme

---

## ⚙️ **Code Standards**

* Functional components only
* React Hooks (`useState`, `useEffect`)
* React Router for navigation
* Centralized API service file
* No backend logic hardcoding

---

## 🎯 **Expected Output**

* Fully working **frontend React app inside `Frontend/` folder**
* Clean, modular, readable code
* Ready for backend API integration
* Production-ready UI structure

---

