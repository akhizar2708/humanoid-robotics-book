// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AI-Driven Humanoid Robotics',
  tagline: 'A Comprehensive Guide to Building Intelligent Robotic Systems',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-username.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'your-username', // Usually your GitHub org/user name.
  projectName: 'hackathon', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Custom fields for environment variables
  customFields: {
    REACT_APP_API_URL: process.env.REACT_APP_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/', // Docs-only mode - docs are at the root
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://github.com/your-username/ai-humanoid-robotics-book/tree/main/',
        },
        blog: false, // Disable blog
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/logo.svg',
      metadata: [
        {name: 'keywords', content: 'robotics, AI, humanoid robots, ROS 2, computer vision, machine learning, motion planning'},
        {name: 'description', content: 'A comprehensive guide to building intelligent humanoid robotic systems with ROS 2, computer vision, and AI'},
        {name: 'author', content: 'AI-Driven Humanoid Robotics Team'},
      ],
      navbar: {
        title: 'AI-Driven Humanoid Robotics',
        logo: {
          alt: 'AI-Driven Humanoid Robotics Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Book',
          },
          {
            href: 'https://github.com/your-username/ai-humanoid-robotics-book',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Book Modules',
            items: [
              {
                label: 'Module 1: The Robotic Nervous System',
                to: '/module-1/chapter-1',
              },
              // Uncomment when modules are ready
              // {
              //   label: 'Module 2: Perception and Computer Vision',
              //   to: '/module-2',
              // },
              // {
              //   label: 'Module 3: Motion Planning and Control',
              //   to: '/module-3',
              // },
              // {
              //   label: 'Module 4: Integration and Deployment',
              //   to: '/module-4',
              // },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'ROS 2 Documentation',
                href: 'https://docs.ros.org/en/rolling/',
              },
              {
                label: 'OpenAI Platform',
                href: 'https://platform.openai.com/',
              },
              {
                label: 'Qdrant Vector Database',
                href: 'https://qdrant.tech/documentation/',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub Repository',
                href: 'https://github.com/your-username/hackathon',
              },
              {
                label: 'Report Issues',
                href: 'https://github.com/your-username/hackathon/issues',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} AI-Driven Humanoid Robotics. Built with Docusaurus and powered by AI.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'bash', 'json', 'yaml', 'sql'],
      },
    }),
};

module.exports = config;
