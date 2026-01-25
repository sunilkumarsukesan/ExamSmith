import React, { useState } from 'react';
import './Contact.css';
import { FaPhone, FaEnvelope, FaMapMarkerAlt } from 'react-icons/fa';

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });

  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Form submission logic would go here
    console.log('Form submitted:', formData);
    setSubmitted(true);
    setFormData({ name: '', email: '', message: '' });
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <div className="contact">
      <div className="contact-hero">
        <h1>Contact Us</h1>
        <p>We'd love to hear from you. Get in touch with us today!</p>
      </div>

      <div className="contact-container">
        <div className="contact-info">
          <h2>Get In Touch</h2>
          
          <div className="info-item">
            <FaPhone className="info-icon" />
            <div>
              <h3>Phone</h3>
              <p>+1 (555) 123-4567</p>
            </div>
          </div>

          <div className="info-item">
            <FaEnvelope className="info-icon" />
            <div>
              <h3>Email</h3>
              <p>support@examsmith.com</p>
            </div>
          </div>

          <div className="info-item">
            <FaMapMarkerAlt className="info-icon" />
            <div>
              <h3>Location</h3>
              <p>123 Education Street, Learning City, LC 12345</p>
            </div>
          </div>
        </div>

        <form className="contact-form" onSubmit={handleSubmit}>
          <h2>Send us a Message</h2>
          
          <div className="form-group">
            <label htmlFor="name">Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Your name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="message">Message *</label>
            <textarea
              id="message"
              name="message"
              value={formData.message}
              onChange={handleChange}
              required
              placeholder="Your message"
              rows="5"
            ></textarea>
          </div>

          <button type="submit" className="submit-btn">Send Message</button>

          {submitted && (
            <div className="success-message">
              ✓ Thank you! Your message has been sent successfully.
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
