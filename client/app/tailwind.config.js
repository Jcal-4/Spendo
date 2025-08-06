// tailwind.config.js

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        './build/**/*.{html,js,jsx}',
        './postcss.config.cjs',
        './src/**/*.{html,js,jsx}',
    ],
    theme: {
        extend: {
            colors: {
                customBlue: '#66fcf1',
            },
            fontSize: {
                'xxs-custom': '9.5px',
            },
        },
    },
    darkMode: 'false',
    plugins: []
};
