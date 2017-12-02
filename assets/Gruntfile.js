module.exports = function(grunt) {

  var theme = function (name) {
    var files = {}
    files['../supervisr/core/static/css/' + name + '.theme.css'] = 'less/' + name + '.theme.less';
    return {
      options: {
        style: 'expanded',
        paths: ['node_modules', '.'],
      },
      files: files
    };
  };

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
        sourceMap: true,
      },
      supervisr: {
        src: [
            'node_modules/clarity-icons/clarity-icons.min.js',
            'node_modules/jquery/dist/jquery.js',
            'node_modules/tablesorter/dist/js/jquery.tablesorter.js',
            'js/*.js',
        ],
        dest: '../supervisr/core/static/js/app.min.js',
      },
    },
    less: {
      light: theme('light'),
      dark: theme('dark'),
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
      },
      image_doc: {
        files: [
          { expand: true, cwd: 'img', src: ['icon.png', 'icon_white.png'], dest: '../docs/img/'},
        ]
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-npm-command');
  grunt.loadNpmTasks('grunt-contrib-copy');

  grunt.registerTask('default', ['uglify', 'less', 'copy']);

};
