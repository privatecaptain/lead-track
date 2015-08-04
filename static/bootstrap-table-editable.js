/**
 * @author zhixin wen <wenzhixin2010@gmail.com>
 * extensions: https://github.com/vitalets/x-editable
 */

!function ($) {

    'use strict';

    $.extend($.fn.bootstrapTable.defaults, {
        editable: true,
        onEditableInit: function () {
            return false;
        },
        onEditableSave: function (field, row, oldValue, $el) {
            return false;
        }
    });

    $.extend($.fn.bootstrapTable.Constructor.EVENTS, {
        'editable-init.bs.table': 'onEditableInit',
        'editable-save.bs.table': 'onEditableSave'
    });

    var BootstrapTable = $.fn.bootstrapTable.Constructor,
        _initTable = BootstrapTable.prototype.initTable,
        _initBody = BootstrapTable.prototype.initBody;

    BootstrapTable.prototype.initTable = function () {
        $.fn.editable.defaults.mode = 'inline';
        var status;
        var agent;
        $.ajax({
            url:"/status",
            success: function(data) {
                // body...
                status = data;
            }
        });
        $.ajax({
            url:"/agents",
            success: function(data) {
                // body...
                agent = data;
            }
        });

        var that = this;
        _initTable.apply(this, Array.prototype.slice.apply(arguments));

        if (!this.options.editable) {
            return;
        }

        $.each(this.columns, function (i, column) {
            if (!column.editable) {
                return;
            }

            var _formatter = column.formatter;
            column.formatter = function (value, row, index) {
                var result = _formatter ? _formatter(value, row, index) : value;
                if (column.field == 'lead_id') {
                        console.log(column.lead_id)
                        return ['<a href="/profile?lead_id=' + row.lead_id +'"><i class="glyphicon glyphicon-eye-open"></i></a>']
                }
                if (column.typo == 'select') {

                        return ['<a href="javascript:void(0)"',
                        ' data-name="' + column.field + '"',
                        ' data-url="/edit"',
                        ' data-type="'+ column.typo + '"',
                        ' data-emptytext="' + column.field + '"',
                        ' data-pk="' + row.lead_id + '"',        
                       'data-value="' + result + '"',
                       ' data-source="' + eval(column.field) + '"',
                        '>' + '</a>'
                    ].join('');
                }
                else{

                    return ['<a href="javascript:void(0)"',
                        ' data-name="' + column.field + '"',
                        ' data-url="/edit"',
                        ' data-type="'+ column.typo + '"',
                        ' data-pk="' + row.lead_id + '"',        
                       'data-value="' + result + '"',
                        '>' + '</a>'
                    ].join('');

                }
            };
        });
    };

    BootstrapTable.prototype.initBody = function () {
        var that = this;
        _initBody.apply(this, Array.prototype.slice.apply(arguments));

        if (!this.options.editable) {
            return;
        }

        $.each(this.columns, function (i, column) {
            if (!column.editable) {
                return;
            }

            that.$body.find('a[data-name="' + column.field + '"]').editable(column.editable)
                .off('save').on('save', function (e, params) {
                    var data = that.getData(),
                        index = $(this).parents('tr[data-index]').data('index'),
                        row = data[index],
                        oldValue = row[column.field];

                    row[column.field] = params.submitValue;
                    that.trigger('editable-save', column.field, row, oldValue, $(this));
                });
        });
        this.trigger('editable-init');
        // console.log('Yeah');
        $(function () {
          $table.bootstrapTable('checkAll');
              var checks = {field: 'lead_id',
                            values: getIdSelections()}
              // console.log(checks);
              $table.bootstrapTable('uncheckBy',checks);

});
    };
                            
}(jQuery);
