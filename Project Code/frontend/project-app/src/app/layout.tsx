import React from "react";
import { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <style>{`
          html, body {
            background: linear-gradient(135deg, #181c24 0%, #23283a 100%);
            color: #f3f3f3;
            font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif;
            min-height: 100vh;
            margin: 0;
            padding: 0;
            letter-spacing: 0.01em;
          }
          .action-btn {
            background: linear-gradient(90deg, #00e0ff 0%, #00ffa3 100%);
            color: #181c24;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.7rem;
            font-size: 1.08rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 2px 8px #00e0ff33;
            transition: background 0.2s, color 0.2s, transform 0.1s;
            outline: none;
          }
          .action-btn:hover, .action-btn:focus {
            background: linear-gradient(90deg, #00ffa3 0%, #00e0ff 100%);
            color: #181c24;
            transform: translateY(-2px) scale(1.04);
            box-shadow: 0 4px 16px #00ffa355;
          }
          .stop-btn {
            background: #ff2d55;
            color: #fff;
            font-weight: 700;
            font-size: 1.1rem;
            border: none;
            border-radius: 8px;
            box-shadow: 0 2px 8px #ff2d5533;
            letter-spacing: 1px;
            transition: background 0.2s, transform 0.1s;
            cursor: pointer;
          }
          .stop-btn:hover, .stop-btn:focus {
            background: #ff1744;
            color: #fff;
            transform: translateY(-2px) scale(1.04);
            box-shadow: 0 4px 16px #ff2d5555;
          }
          .spinner {
            display: inline-block;
            width: 28px;
            height: 28px;
            border: 4px solid #444;
            border-top: 4px solid #00e0ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          input, textarea, select {
            background: #181c24;
            color: #fff;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 0.4rem 0.7rem;
            font-size: 1rem;
            margin-top: 0.2rem;
            margin-bottom: 0.5rem;
            outline: none;
            transition: border 0.2s, box-shadow 0.2s;
          }
          input:focus, textarea:focus, select:focus {
            border: 1.5px solid #00e0ff;
            box-shadow: 0 0 0 2px #00e0ff33;
          }
          label {
            color: #b8e0ff;
            font-weight: 500;
            margin-bottom: 0.2rem;
          }
          ::selection {
            background: #00e0ff55;
          }
          a {
            color: #00e0ff;
            text-decoration: none;
            transition: color 0.2s;
          }
          a:hover, a:focus {
            color: #00ffa3;
            text-decoration: underline;
          }
        `}</style>
      </body>
    </html>
  );
}
