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
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      supervisr: {
        src: [
            'node_modules/clarity-icons/clarity-icons.min.js',
            'node_modules/jquery/dist/jquery.js',
            'js/*.js',
        ],
        dest: '../supervisr/core/static/app.min.js',
      },
    },
    cssmin: {
      supervisr: {
        files: [{
          src: [
              'node_modules/clarity-icons/clarity-icons.min.css',
              'node_modules/clarity-ui/clarity-ui.min.css',
              'css/*.css',
          ],
          dest: '../supervisr/core/static/app.min.css',
        }]
      }
    },
    copy: {
      custom_elements: {
        files: [
          { src: ['node_modules/@webcomponents/custom-elements/custom-elements.min.js'],
            dest: '../supervisr/core/static/custom-elements.min.js'}
        ]
      },
      images: {
        files: [
          { expand: true, cwd: 'img', src: ['*'], dest: '../supervisr/core/static/img/' },
        ]
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-npm-command');
  grunt.loadNpmTasks('grunt-contrib-copy');

  grunt.registerTask('default', ['npm-command', 'uglify', 'cssmin', 'copy']);

};
