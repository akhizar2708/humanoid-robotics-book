---
sidebar_position: 1
slug: /
---

import styles from './intro.module.css';

<div className={styles.heroSection}>
  <div className={styles.heroContent}>
    <div className={styles.heroBadge}>
      <span className={styles.badgeIcon}>🤖</span>
      <span>AI-Powered Robotics Education</span>
    </div>
    <h1 className={styles.heroTitle}>
      Master AI-Driven<br/>
      <span className={styles.gradientText}>Humanoid Robotics</span>
    </h1>
    <p className={styles.heroSubtitle}>
      A comprehensive, hands-on guide to building intelligent robotic systems using ROS 2,
      computer vision, and cutting-edge AI techniques. From fundamentals to deployment.
    </p>
    <div className={styles.heroCTA}>
      <a href="/module-1/chapter-1" className={styles.primaryButton}>
        Start Learning
        <span className={styles.buttonIcon}>→</span>
      </a>
      <a href="#features" className={styles.secondaryButton}>
        Explore Features
      </a>
    </div>
    <div className={styles.heroStats}>
      <div className={styles.statItem}>
        <div className={styles.statNumber}>4</div>
        <div className={styles.statLabel}>Modules</div>
      </div>
      <div className={styles.statItem}>
        <div className={styles.statNumber}>12+</div>
        <div className={styles.statLabel}>Chapters</div>
      </div>
      <div className={styles.statItem}>
        <div className={styles.statNumber}>50+</div>
        <div className={styles.statLabel}>Code Examples</div>
      </div>
    </div>
  </div>
</div>

<div id="features" className={styles.featuresSection}>
  <div className={styles.sectionHeader}>
    <h2 className={styles.sectionTitle}>What You'll Master</h2>
    <p className={styles.sectionSubtitle}>
      Everything you need to build production-ready humanoid robotic systems
    </p>
  </div>

  <div className={styles.featureGrid}>
    <div className={styles.featureCard}>
      <div className={styles.featureIcon}>🧠</div>
      <h3 className={styles.featureTitle}>ROS 2 Architecture</h3>
      <p className={styles.featureDesc}>
        Build the robotic nervous system with ROS 2, mastering nodes, topics, services,
        and real-time control systems.
      </p>
      <a href="/module-1/chapter-1" className={styles.featureLink}>
        Learn more →
      </a>
    </div>

    <div className={styles.featureCard}>
      <div className={styles.featureIcon}>👁️</div>
      <h3 className={styles.featureTitle}>Computer Vision</h3>
      <p className={styles.featureDesc}>
        Implement advanced perception systems using OpenCV, depth sensing, and
        neural networks for object recognition.
      </p>
      <a href="#" className={styles.featureLink}>
        Learn more →
      </a>
    </div>

    <div className={styles.featureCard}>
      <div className={styles.featureIcon}>🎯</div>
      <h3 className={styles.featureTitle}>Motion Planning</h3>
      <p className={styles.featureDesc}>
        Master path planning algorithms, inverse kinematics, and control theory
        for smooth robotic movement.
      </p>
      <a href="#" className={styles.featureLink}>
        Learn more →
      </a>
    </div>

    <div className={styles.featureCard}>
      <div className={styles.featureIcon}>🚀</div>
      <h3 className={styles.featureTitle}>Deployment</h3>
      <p className={styles.featureDesc}>
        Take your robots from prototype to production with containerization,
        monitoring, and cloud integration.
      </p>
      <a href="#" className={styles.featureLink}>
        Learn more →
      </a>
    </div>
  </div>
</div>

<div className={styles.aiSection}>
  <div className={styles.aiContent}>
    <div className={styles.aiIconWrapper}>
      <div className={styles.aiIconPulse}></div>
      <span className={styles.aiIcon}>💬</span>
    </div>
    <div className={styles.aiText}>
      <h2 className={styles.aiTitle}>AI-Powered Learning Assistant</h2>
      <p className={styles.aiDescription}>
        Get instant answers to your questions with our intelligent chatbot. Ask about concepts,
        debug code, or explore topics in depth - all powered by advanced AI.
      </p>
      <ul className={styles.aiFeatures}>
        <li>✓ Contextual answers from the book content</li>
        <li>✓ Code examples and explanations</li>
        <li>✓ Interactive problem solving</li>
      </ul>
      <button className={styles.aiButton} onClick={() => {
        const chatButton = document.querySelector('[aria-label="Open chat"]');
        if (chatButton) chatButton.click();
      }}>
        Try the AI Assistant
      </button>
    </div>
  </div>
</div>

<div className={styles.prerequisitesSection}>
  <h2 className={styles.sectionTitle}>Prerequisites</h2>
  <div className={styles.prereqGrid}>
    <div className={styles.prereqItem}>
      <div className={styles.prereqIcon}>💻</div>
      <div className={styles.prereqContent}>
        <h4>Programming</h4>
        <p>Python and C++ basics</p>
      </div>
    </div>
    <div className={styles.prereqItem}>
      <div className={styles.prereqIcon}>📐</div>
      <div className={styles.prereqContent}>
        <h4>Mathematics</h4>
        <p>Linear algebra & calculus</p>
      </div>
    </div>
    <div className={styles.prereqItem}>
      <div className={styles.prereqIcon}>⚙️</div>
      <div className={styles.prereqContent}>
        <h4>Robotics (Optional)</h4>
        <p>Helpful but not required</p>
      </div>
    </div>
  </div>
</div>

<div className={styles.ctaSection}>
  <h2 className={styles.ctaTitle}>Ready to Build Intelligent Robots?</h2>
  <p className={styles.ctaSubtitle}>
    Start your journey into the future of robotics and AI
  </p>
  <a href="/module-1/chapter-1" className={styles.ctaButton}>
    Begin Chapter 1
    <span className={styles.buttonIcon}>→</span>
  </a>
</div>
