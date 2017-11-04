module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    'npm-command': {
      install: {
        cmd: 'install',
      },
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
        sourceMap: true,
      },
      supervisr: {
        src: [
            'node_modules/clarity-icons/clarity-icons.min.js',
            'node_modules/jquery/dist/jquery.js',
            'js/*.js',
        ],
        dest: '../supervisr/core/static/js/app.min.js',
      },
    },
    cssmin: {
      supervisr: {
        sourceMap: true,
        files: [{
          src: [
              'node_modules/clarity-icons/clarity-icons.min.css',
              'node_modules/clarity-ui/clarity-ui.min.css',
              'node_modules/font-awesome/css/font-awesome.min.css',
              'css/*.css',
          ],
          dest: '../supervisr/core/static/css/app.min.css',
        }],
      }
    },
    copy: {
      custom_elements: {
        files: [
          { src: ['node_modules/@webcomponents/custom-elements/custom-elements.min.js'],
            dest: '../supervisr/core/static/js/custom-elements.min.js'},
          { src: ['node_modules/@webcomponents/custom-elements/custom-elements.min.js.map'],
            dest: '../supervisr/core/static/js/custom-elements.min.js.map'}
        ]
      },
      raven: {
        files: [
          { src: ['node_modules/raven-js/dist/raven.min.js'],
            dest: '../supervisr/core/static/js/raven.min.js'},
          { src: ['node_modules/raven-js/dist/raven.min.js.map'],
            dest: '../supervisr/core/static/js/raven.min.js.map'},
        ]
      },
      images: {
        files: [
          { expand: true, cwd: 'img', src: ['*'], dest: '../supervisr/core/static/img/' },
        ]
      },
      fonts: {
        files: [
          { expand: true, cwd: 'node_modules/font-awesome/fonts/', src: ['*'], dest: '../supervisr/core/static/fonts/' },
        ]
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-npm-command');
  grunt.loadNpmTasks('grunt-contrib-copy');

  grunt.registerTask('default', ['uglify', 'cssmin', 'copy']);

};
