/*
 * Copyright (c) 2016 VMware, Inc. All Rights Reserved.
 * This software is released under MIT license.
 * The full license information can be found in LICENSE in the root directory of this project.
 */
"use strict";
var iconShapeSources = {};
var ClarityIconsApi = (function () {
    function ClarityIconsApi() {
    }
    Object.defineProperty(ClarityIconsApi, "instance", {
        get: function () {
            if (!ClarityIconsApi.singleInstance) {
                ClarityIconsApi.singleInstance = new ClarityIconsApi();
            }
            return ClarityIconsApi.singleInstance;
        },
        enumerable: true,
        configurable: true
    });
    ClarityIconsApi.prototype.validateName = function (name) {
        if (name.length === 0) {
            throw new Error("Shape name or alias must be a non-empty string!");
        }
        if (/\s/.test(name)) {
            throw new Error("Shape name or alias must not contain any whitespace characters!");
        }
        return true;
    };
    ClarityIconsApi.prototype.validateTemplate = function (template) {
        if (!template.startsWith("<svg") || !template.endsWith("</svg>")) {
            throw new Error("Template must be SVG markup!");
        }
        return true;
    };
    ClarityIconsApi.prototype.setIconTemplate = function (shapeName, shapeTemplate) {
        var trimmedShapeTemplate = shapeTemplate.trim();
        if (this.validateName(shapeName) && this.validateTemplate(trimmedShapeTemplate)) {
            //if the shape name exists, delete it.
            if (iconShapeSources[shapeName]) {
                delete iconShapeSources[shapeName];
            }
            iconShapeSources[shapeName] = trimmedShapeTemplate;
        }
    };
    ClarityIconsApi.prototype.setIconAliases = function (templates, shapeName, aliasNames) {
        for (var _i = 0, aliasNames_1 = aliasNames; _i < aliasNames_1.length; _i++) {
            var aliasName = aliasNames_1[_i];
            if (this.validateName(aliasName)) {
                Object.defineProperty(templates, aliasName, {
                    get: function () {
                        return templates[shapeName];
                    },
                    enumerable: true,
                    configurable: true
                });
            }
        }
    };
    ClarityIconsApi.prototype.add = function (icons) {
        if (typeof icons !== "object") {
            throw new Error("The argument must be an object literal passed in the following pattern: \n                { \"shape-name\": \"shape-template\" }");
        }
        for (var shapeName in icons) {
            if (icons.hasOwnProperty(shapeName)) {
                this.setIconTemplate(shapeName, icons[shapeName]);
            }
        }
    };
    ClarityIconsApi.prototype.get = function (shapeName) {
        //if shapeName is not given, return all icon templates.
        if (!shapeName) {
            return iconShapeSources;
        }
        if (typeof shapeName !== "string") {
            throw new TypeError("Only string argument is allowed in this method.");
        }
        //if shapeName doesn't exist in the icons templates, throw an error.
        if (!iconShapeSources[shapeName]) {
            throw new Error("'" + shapeName + "' is not found in the Clarity Icons set.");
        }
        return iconShapeSources[shapeName];
    };
    ClarityIconsApi.prototype.alias = function (aliases) {
        if (typeof aliases !== "object") {
            throw new Error("The argument must be an object literal passed in the following pattern: \n                { \"shape-name\": [\"alias-name\", ...] }");
        }
        for (var shapeName in aliases) {
            if (aliases.hasOwnProperty(shapeName)) {
                if (iconShapeSources.hasOwnProperty(shapeName)) {
                    //set an alias to the icon if it exists in iconShapeSources.
                    this.setIconAliases(iconShapeSources, shapeName, aliases[shapeName]);
                }
                else if (iconShapeSources.hasOwnProperty(shapeName)) {
                    //set an alias to the icon if it exists in iconShapeSources.
                    this.setIconAliases(iconShapeSources, shapeName, aliases[shapeName]);
                }
                else {
                    throw new Error("The icon '" + shapeName + "' you are trying to set an alias to doesn't exist!");
                }
            }
        }
    };
    return ClarityIconsApi;
}());
exports.ClarityIconsApi = ClarityIconsApi;
