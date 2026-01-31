# ExamSmith Frontend

AI-Powered Question Paper Generation Platform - React Frontend Application

## Overview

ExamSmith Frontend is a modern, responsive React application built with Vite and Tailwind CSS. It provides a complete user interface for students, teachers, and administrators to manage exam questions and question papers.

## Features

### 🎓 Student Features
- Generate custom question papers with AI
- Practice with generated questions
- Track performance and progress
- Download/Print question papers
- Evaluate answers in real-time

### 👨‍🏫 Teacher Features
- Create and manage question papers
- Review student papers
- Access performance analytics
- Customize difficulty levels and topics
- Manage question repository

### 🛠️ Admin Features
- User management system
- System configuration
- Security settings
- Monitor platform statistics
- 2FA and password policies

### 🌐 General Features
- Responsive design (mobile, tablet, desktop)
- Clean and modern UI/UX
- Navigation bar and footer
- Multiple role-based dashboards
- Contact form
- About page

## Tech Stack

- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.8
- **Styling**: Tailwind CSS 3.3.6
- **Routing**: React Router DOM 6.20.0
- **Icons**: React Icons 4.12.0
- **HTTP Client**: Axios 1.6.2
- **CSS Processing**: PostCSS & Autoprefixer

## Project Structure

```
Frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/            # Images, fonts, etc.
│   ├── components/        # Reusable components
│   │   ├── Navbar.jsx     # Navigation bar
│   │   ├── Footer.jsx     # Footer component
│   │   └── RoleCard.jsx   # Role selection cards
│   ├── pages/             # Page components
│   │   ├── Home.jsx       # Homepage
│   │   ├── About.jsx      # About page
│   │   ├── Contact.jsx    # Contact page
│   │   ├── SignIn.jsx     # Sign in page
│   │   ├── Student.jsx    # Student dashboard
│   │   ├── Teacher.jsx    # Teacher dashboard
│   │   └── Admin.jsx      # Admin dashboard
│   ├── services/
│   │   └── api.js         # API service client
│   ├── App.jsx            # Main app component
│   ├── App.css            # Global styles
│   ├── index.css          # Tailwind CSS
│   └── main.jsx           # React entry point
├── index.html             # HTML entry point
├── package.json           # Dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
└── README.md              # This file
```

## Installation

### Prerequisites
- Node.js 16.x or higher
- npm 8.x or higher

### Setup

1. Navigate to the Frontend directory:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file for API configuration:
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

## Running the Application

### Development Mode
```bash
npm run dev
```
The application will start on `http://localhost:3000` with hot module reloading.

### Production Build
```bash
npm run build
```
Builds the application for production in the `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

## API Integration

The frontend communicates with the backend using the API service in `src/services/api.js`.

### Available API Functions

- `generateQuestionPaper(params)` - Generate a new question paper
- `askQuestion(question, hybridSearch)` - Ask a question and get answers
- `findSimilarQuestions(questionText, topK, difficulty)` - Find similar questions
- `evaluateAnswer(questionText, studentAnswer, questionId)` - Evaluate student answers
- `checkHealth()` - Check backend health status

### Example Usage

```javascript
import { generateQuestionPaper } from './services/api';

const handleGeneratePaper = async () => {
  try {
    const response = await generateQuestionPaper({
      difficulty: 'medium',
      totalMarks: 100,
      subject: 'english'
    });
    console.log(response);
  } catch (error) {
    console.error('Error:', error);
  }
};
```

## Pages and Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | Home | Landing page with role selection |
| `/about` | About | Information about the platform |
| `/contact` | Contact | Contact form and information |
| `/signin` | SignIn | User authentication page |
| `/student` | Student | Student dashboard and paper generation |
| `/teacher` | Teacher | Teacher's question paper management |
| `/admin` | Admin | Admin dashboard and system management |

## Components

### Navbar
- Responsive navigation bar with hamburger menu
- Logo and branding
- Navigation links
- Sign-in button

### Footer
- Company information
- Quick links
- Social media icons
- Copyright notice

### RoleCard
- Role selection cards with icons
- Hover effects and animations
- Navigation to role-specific dashboards

## Styling

The application uses Tailwind CSS for utility-first styling with custom configuration:

- **Primary Color**: #667eea (Blue-Purple)
- **Secondary Color**: #764ba2 (Purple)
- **Accent Color**: #7c3aed (Violet)

### Custom CSS

Custom CSS files are provided for complex components:
- `components/Navbar.css`
- `components/Footer.css`
- `components/RoleCard.css`
- `pages/*.css`

## Responsive Design

The application is fully responsive with breakpoints at:
- 768px (tablets)
- Mobile-first approach

All components adapt gracefully to different screen sizes.

## State Management

Currently uses React Hooks (`useState`, `useEffect`) for state management. For larger applications, consider:
- Redux
- Context API
- Zustand

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting with React Router
- Lazy loading where appropriate
- Optimized images and assets
- CSS-in-JS with Tailwind for smaller bundle size

## Development Guidelines

### Code Style
- Use functional components
- Use React Hooks
- Proper component naming conventions
- Props validation (optional, consider PropTypes or TypeScript)

### Naming Conventions
- Components: PascalCase (e.g., `UserProfile.jsx`)
- Files: PascalCase for components, lowercase for utilities
- Classes/IDs: kebab-case
- Variables: camelCase

### Best Practices
- Keep components small and focused
- Reuse components where possible
- Separate concerns (components, services, utilities)
- Add comments for complex logic
- Use meaningful variable and function names

## Troubleshooting

### Common Issues

**Port 3000 already in use:**
```bash
npm run dev -- --port 3001
```

**Module not found:**
```bash
npm install
```

**Hot reload not working:**
- Check if Vite server is running
- Restart the development server

## Future Enhancements

- [ ] Add TypeScript support
- [ ] Implement proper authentication
- [ ] Add Redux for state management
- [ ] Implement real-time notifications
- [ ] Add dark mode
- [ ] Implement PWA features
- [ ] Add unit and integration tests
- [ ] Implement internationalization (i18n)

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Create a pull request

## License

MIT License

## Support

For issues and questions, please contact support@examsmith.com

---

**Built with ❤️ for better education**
