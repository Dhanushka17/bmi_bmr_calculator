# Health Check Application

A Flask web application for calculating and understanding BMI and BMR health metrics.

## Features

- BMI Calculator
- BMR Calculator
- Sustainable Engineering and Health
- Pros and Cons of BMI and BMR

## Deployment on Vercel

This application is configured for deployment on Vercel. Follow these steps to deploy:

1. **Install Vercel CLI**:
   ```
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```
   vercel login
   ```

3. **Deploy the application**:
   ```
   vercel
   ```

4. **For production deployment**:
   ```
   vercel --prod
   ```

Alternatively, you can deploy directly from the Vercel dashboard:

1. Create a new account or login at [vercel.com](https://vercel.com)
2. Create a new project and import your repository
3. Vercel will automatically detect the Flask application
4. Configure your project settings and deploy

## Local Development

To run the application locally:

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your browser and navigate to `http://localhost:5000`

