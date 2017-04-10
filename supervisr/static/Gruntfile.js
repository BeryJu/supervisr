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
        dest: 'build/app.min.js',
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
          dest: 'build/app.min.css',
        }]
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-npm-command');

  grunt.registerTask('default', ['npm-command', 'uglify', 'cssmin']);

};
