const path = require('path');

module.exports = {
  entry: './src/main.jsx',  
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.css$/,
        loader: ['style-loader', 'css-loader']
      }      
    ]
  },
  output: {
    path: path.resolve(__dirname, 'app/static/js'),
    filename: 'main.js'
  }  
};
