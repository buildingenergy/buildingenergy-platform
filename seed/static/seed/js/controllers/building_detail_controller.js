/**
 * :copyright: (c) 2014 Building Energy Inc
 * :license: see LICENSE for more details.
 */
angular.module('BE.seed.controller.buiding_detail', [])
.controller('building_detail_controller', [
  '$scope',
  '$routeParams',
  '$modal',
  '$log',
  'building_services',
  'project_service',
  'building_payload',
  'all_columns',
  'audit_payload',
  'urls',
  '$filter',
  '$location',
  'audit_service',
  function($scope, $routeParams, $modal, $log, building_services, project_service, building_payload, all_columns, audit_payload, urls, $filter, $location, audit_service) {
    $scope.user = {};
    $scope.user.building_id = $routeParams.building_id;
    $scope.user.project_slug = $routeParams.project_id;
    $scope.projects = [];
    $scope.labels = [];
    $scope.building = building_payload.building;
    $scope.building.businesses = $scope.building.businesses || [];
    $scope.building.meters = $scope.building.meters || [];
    $scope.user_role = building_payload.user_role;
    $scope.user_org_id = building_payload.user_org_id;
    $scope.building.recent_sale_date = $filter('date')($scope.building.recent_sale_date, 'MM/dd/yyyy');
    $scope.imported_buildings = building_payload.imported_buildings;
    $scope.projects = building_payload.projects;
    $scope.fields = all_columns.fields;
    $scope.building_copy = {};
    $scope.extra_data_columns = [];
    $scope.contact_types = [
      'Owner',
      'Property Manager',
      'Occupant',
      'Energy Auditor',
      'Energy Modeler',
      'Contractor',
      'Other'
    ];
    $scope.contact_type = $scope.contact_types[0];
    $scope.data_columns = [];
    $scope.audit_logs = audit_payload.audit_logs;
    // set the tab
    $scope.section = $location.hash();
    /**
     * label section
     */

    $scope.status = {
        isopen: false
    };

    /**
     * get_label: returns a building's label or a default
     */
    $scope.get_label = function(building) {
        // helper function to get a label for a building or return a
        // default the label doesn't exist
        if (typeof building.label === "undefined") {
            return {
                'name': 'Add Label',
                'label': 'default'
            };
        }
        return building.label;
    };

    /**
     * get_labels: gets all labels for a user's org, called by init()
     */
    var get_labels = function() {
        // gets all labels for an org user
        project_service.get_labels().then(function(data) {
            // resolve promise
            $scope.labels = data.labels;
        });
    };

    /**
     * remove_label: removes a label from a project building, on success calls
     *   init() to refresh the list of project buildings from the server
     */
    $scope.remove_label = function(project) {
        project_service.remove_label(project, $scope.building).then(function(data){
            // resolve promise
            init();
            delete(project.building.label);
        }, function(data, status){
            // reject promise
            console.log({data: data, status: status});
        });
    };

    /**
     * open_edit_label_modal: opens the edit label modal, on close or dismiss
     *   init() is called to refresh available labels
     */
    $scope.open_edit_label_modal = function() {
        var modalInstance = $modal.open({
            templateUrl: urls.static_url + 'seed/partials/manage_labels_modal.html',
            controller: 'edit_label_modal_ctrl',
            resolve: {
                labels: function () {
                    return $scope.labels;
                }
            }
        });

        modalInstance.result.then(
            function () {
                init();
        }, function (message) {
                $log.info(message);
                $log.info('Modal dismissed at: ' + new Date());
                init();
        });
    };
    /**
     * end label section
     */

    /**
     * is_project: returns true is building breadcrumb is from a project, used
     *   to hide/show the project breadcrumb url, i.e. return to all buildings
     *   or a project.
     */
    $scope.is_project = function() {
        if (typeof $scope.user.project_slug === "undefined") {
            return false;
        } else {
            return true;
        }
    };

    /**
     * is_active_project: returns true if `project` is the project breadcrumb.
     *   Used to highlight the table row for the active project in a list of
     *   compliance projects
     */
    $scope.is_active_project = function(project) {
        var p = $scope.project || {};
        return p.id === project.id;
    };


    /**
     * has_projects: used to show a custom table in the case no projects exist
     *   for a user's org.
     */
    $scope.user.has_projects = function() {
        // return true if user has any projects
        try {
            return $scope.projects.length > 0;
        } catch(err) {
            console.log(err);
            return false;
        }
    };

    /**
     * update_project_building: adds or updates a label for on the the project-
     *   buildings. Since a building can have different labels across projects,
     *   the project is used to determine the correct project-building.
     */
    $scope.update_project_building = function(project, label) {
        project_service.update_project_building($scope.building.pk, project.slug, label).then(function(data){
            // resolve promise
            project.building.approver = data.approver;
            project.building.approved_date = data.approved_date;
            project.building.label = label;
        }, function(data, status) {
            // reject promise
            console.log({data: data, status: status});
        });
    };

    /**
     * set_building_attribute: sets the building attribute from a star click
     */
    $scope.set_building_attribute = function (parent, field_name, extra_data) {
        var f = field_name.key || field_name;
        if (typeof extra_data !== "undefined" && extra_data){
            $scope.building.extra_data[f] = parent.extra_data[f];
            $scope.building.extra_data_sources[f] = parent.id;
        } else {
            $scope.building[f] = parent[f];
            $scope.building[f + '_source'] = parent.id;
        }
        // turn of master source star if set on another file
        if (!parent.is_master) {
            angular.forEach($scope.imported_buildings, function (b) {
                b.is_master = false;
            });
        }
    };

    /**
     * save_building_state: saves the building state in case cancel gets clicked
     */
    $scope.save_building_state = function () {
        $scope.building_copy = angular.copy($scope.building);
    };

    /**
     * restore_building: restores the building from its copy
     *   and hides the edit fields
     */
    $scope.restore_building = function () {
        $scope.building = $scope.building_copy;
        $scope.building.edit_form_showing = false;
    };

    /**
     * is_valid_key: checks to see if the key or attribute should be excluded
     *   from being copied from parent to master building
     */
    $scope.is_valid_key = function (key) {
        var known_invalid_keys = [
            'best_guess_confidence',
            'best_guess_canonical_building',
            'canonical_building',
            'canonical_for_ds',
            'children',
            'confidence',
            'created',
            'extra_data',
            'extra_data_sources',
            'id',
            'is_master',
            'import_file',
            'import_file_name',
            'last_modified_by',
            'match_type',
            'modified',
            'model',
            'parents',
            'pk',
            'super_organization',
            'source_type',
            'meters',
            'survey',
            'utilies',
            'natural_gas_provider_account_number',
            'businesses',
            'edit_form_showing',
            'electric_provider',
            'electric_provider_account_number',
            'natural_gas_provider'
        ];
        var no_invalid_key = known_invalid_keys.indexOf(key) === -1;

        return (key.indexOf('_source') === -1 &&
                key.indexOf('extra_data') === -1 && key.indexOf('$$') === -1 &&
                no_invalid_key);
    };

    /**
     * make_source_default: makes one file the default source for all values it
     *   has unless the column does not have a value for a field
     */
    $scope.make_source_default = function (parent) {
        parent.is_master = true;
        // unselect any other master
        angular.forEach($scope.imported_buildings, function(b){
            if (b.id !== parent.id) {
                b.is_master = false;
            }
        });
        // main attributes
        angular.forEach(parent, function (val, key){
            if (val !== null && $scope.is_valid_key(key)){
                $scope.building[key] = val;
                $scope.building[key + '_source'] = parent.id;
            }
        });
        // extra_data
        angular.forEach(parent.extra_data, function (val, key){
            if (val !== null){
                $scope.building.extra_data[key] = val;
                $scope.building.extra_data_sources[key] = parent.id;
            }
        });
    };

    /**
     * save_building: saves the building's updates
     */
    $scope.save_building = function (){
        $scope.$emit('show_saving');
        // remove blank meter time series rows/entries
        var remove_blank_row = function(row) {
            // return if some part of the time series entry is present
            if (row.id !== null ||
                typeof row.cost !== 'undefined' ||
                typeof row.end_time !== 'undefined' ||
                typeof row.reading !== 'undefined'
            ) {
                return row;
            }
        };
        for (var i = 0; i < $scope.building.businesses.length; i++) {
            var business = $scope.building.businesses[i];
            for (var j = 0; j < business.meters.length; j++) {
                var meter = business.meters[i];
                meter.timeseries_data = meter.timeseries_data.filter(remove_blank_row);
            }
        }
        building_services.update_building($scope.building, $scope.user_org_id)
        .then(function (data){
            // resolve promise
            audit_service.get_building_logs($scope.building.canonical_building)
            .then(function(data){
                $scope.audit_logs = data.audit_logs;
            });
            $scope.$emit('finished_saving');
        }, function (data, status){
            // reject promise
            $scope.$emit('finished_saving');
        }).catch(function (data) {
            console.log( String(data) );
        });
    };

    /**
     * set_self_as_source: saves the building's updates. If the optional
     *    ``extra_data`` param is passed and is true, the ``field_name``
     *    attribute will be applied to the building's extra_data attribute and
     *    the building object itself.
     *
     *   ex. $scope.building = {
               gross_floor_area: 12000,
               gross_floor_area_source: 33,
               extra_data: {
                  special_id: 1
               },
               extra_data_sources: {
                  special_id: 33
               },
               id: 10,
               pk: 10
             };

             $scope.set_self_as_source('gross_floor_area', false);
             // $scope.building.gross_floor_area_source is 10

             $scope.set_self_as_source('special_id', true);
             // $scope.building.extra_data.special_id is 10

     *
     * @param {string} field_name: the name of the building attribute
     * @param {bool} extra_data (optional): if true, set the source of the
     *    extra_data attribute
     */
    $scope.set_self_as_source = function (field_name, extra_data){
        if (extra_data) {
            $scope.building.extra_data_sources[field_name] = $scope.building.id;
        } else {
            $scope.building[field_name + '_source'] = $scope.building.id;
        }
        angular.forEach($scope.imported_buildings, function (b) {
            b.is_master = false;
        });
    };


    /**
     * generate_data_columns: sets $scope.data_columns to be a list
     *   of all the data (fixed column and extra_data) fields with non-null
     *   values for $scope.building and each $scope.imported_buildings, which
     *   are concatenated in init() and passed in as param ``buildings``.
     *   Keys/fields are not dupliacated.
     *
     * @param {Array} buildings: concatenated list of buildings
     */
    $scope.generate_data_columns = function(buildings) {
        var key_list = [];
        // handle extra_data
        angular.forEach(buildings, function(b){
            angular.forEach(b.extra_data, function (val, key){
                if (key_list.indexOf(key) === -1 && val !== null){
                    key_list.push(key);
                    $scope.data_columns.push({
                        "key": key,
                        "type": "extra_data"
                    });
                }
            });
        });
        // hanlde building properties
        angular.forEach($scope.building, function ( val, key ) {
            if ( $scope.is_valid_key(key) && val !== null && typeof val !== "undefined" && key_list.indexOf(key) === -1) {
                key_list.push(key);
                $scope.data_columns.push({
                        "key": key,
                        "type": "fixed_column"
                    });
            }
        });
    };

    /**
     * adds a block of html for the user to enter a contact
     */
    $scope.add_contact = function () {
      $scope.building.contacts.push({
        type: $scope.contact_type,
        id: null
      });
      $scope.add_contact_clicked = false;
    };

    /**
     * adds a business to the form
     */
    $scope.add_business = function () {
      $scope.building.businesses.push({
        id: null,
        meters: [],
        contact: {
          id: null,
          contact_type: 'Owner'
        }
      });
    };

    /**
     * adds a meter to a business
     */
    $scope.add_meter = function (business) {
      var meter = {
        id: null,
        energy_type: 'Electricity',
        timeseries_data: []
      };
      for (var i = 0; i < 18; i++) {
        meter.timeseries_data.push({
          id: null
        });
      }
      business.meters.push(meter);
    };

    /**
     * checks if the row has data
     */
    $scope.show_survey_row = function(question) {
      var resp;
      try {
        resp = $scope.building.survey.question_responses[question.id];
      } catch (e) {
        return false;
      }
      if (question.question_type === "Radio" || question.question_type === "Text") {
        if (typeof resp.answer === "undefined" || resp.answer === null || resp.answer.length === 0) {
          return false;
        }
      } else {
        // type === "Enumerated", resp is an object
        if (typeof resp === "undefined" || resp === null || angular.toJson(resp) === "{}") {
          return false;
        }
      }
      return true;
    };

    /**
     * create_note
     */
    $scope.open_create_note_modal = function(existing_note) {
        var modalInstance = $modal.open({
            templateUrl: urls.static_url + 'seed/partials/create_note_modal.html',
            controller: 'create_note_modal_ctrl',
            resolve: {
                building: function () {
                    return $scope.building;
                },
                note: function() {
                    return existing_note;
                }
            }
        });

        modalInstance.result.then(
            function (note) {
                if (typeof existing_note !== 'undefined') {
                    angular.extend(existing_note, note);
                } else {
                    $scope.audit_logs.unshift(note);
                }
        }, function (message) {
                $log.info(message);
        });
    };

    /**
     * sets the ``$scope.section`` var to show the proper tab/section of the
     * page.
     * @param {string} section
     */
    $scope.set_location = function (section) {
        $scope.section = section;
    };

    /**
     * returns a number
     */
    $scope.get_number = function ( num ) {
        if ( !angular.isNumber(num) && num !== null && typeof num !== "undefined") {

            return +num.replace(/,/g, '');
        }
        return num;
    };

    /**
     * init: sets default state of building detail page, gets the breadcrumb
     *   project if exists, sets the field arrays for each section, performs
     *   some date string manipulation for better display rendering, gets
     *   all the org's labels, and gets all the extra_data fields
     *
     */
    var init = function() {
        $scope.building_detail_fields = $scope.fields.filter(function (f) {
            return f.field_type === 'building_information';
        });
        $scope.contact_fields = $scope.fields.filter(function (f) {
            return f.field_type === 'contact_information';
        });
        // find all the floor area fields for the building
        $scope.floor_area_fields = [];
        angular.forEach($scope.building, function(value, key) {
            if (~angular.lowercase(key).indexOf('area') && !~angular.lowercase(key).indexOf('_source')) {
                $scope.floor_area_fields.push({
                    title: key,
                    sort_column: key
                });
            }
        });
        angular.forEach($scope.building.extra_data, function(value, key) {
            if (~angular.lowercase(key).indexOf('area')) {
                $scope.floor_area_fields.push({
                    title: key,
                    sort_column: key,
                    extra_data: true
                });
            }
        });

        $scope.building = building_payload.building;
        $scope.building.recent_sale_date = $filter('date')($scope.building.recent_sale_date, 'MM/dd/yyyy');
        $scope.building.year_ending = $filter('date')($scope.building.year_ending, 'MM/dd/yyyy');
        $scope.building.release_date = $filter('date')($scope.building.release_date, 'MM/dd/yyyy');
        $scope.building.generation_date = $filter('date')($scope.building.generation_date, 'MM/dd/yyyy');
        $scope.building.modified = $filter('date')($scope.building.modified, 'MM/dd/yyyy');
        $scope.building.created = $filter('date')($scope.building.created, 'MM/dd/yyyy');
        $scope.projects = building_payload.projects;
        if ($scope.is_project()){
            project_service.get_project($scope.user.project_slug).then(function(data) {
                    // resolve promise
                    $scope.project = data.project;
                }, function(data, status) {
                    // reject promise
                    console.log({data: data, status: status});
                }
            );
        }
        get_labels();
        $scope.generate_data_columns(
            [$scope.building].concat($scope.imported_buildings)
        );
        // add initail business
        if ($scope.building.businesses.length === 0) {
          $scope.add_business();
        }
    };
    // fired on controller loaded
    init();
}]);
