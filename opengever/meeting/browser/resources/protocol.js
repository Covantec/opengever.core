(function(global, $) {

  "use strict";

  function ProtocolController() {

    global.Controller.call(this);

    var root = $(":root");

    var saveButton = $("#form-buttons-save");
    var protocolControls = $("#protocol-controls");

    var currentMeeting = $(".protocol-navigation").data().meeting;
    var createdAt = new Date($(".protocol-navigation").data().modified).getTime();

    var protocolSynchronizer = new global.Synchronizer({ target: "#content-core input, #content-core select, #content-core textarea", triggers: ["input", "change", "changeDate"] });
    var trixSynchronizer = new global.Synchronizer({ target: "trix-editor", triggers: ["trix-change"] });
    var meetingStorage = new global.MeetingStorage(currentMeeting);

    var showHintForLocalChanges = function() {
      $("#form-buttons-cancel").val($("#button-value-discard").val());
      protocolControls.addClass("local-changes");
    };

    var showHintForConflictChanges = function() {
      root.addClass("conflict-changes");
    };

    var parseProposal = function(expression) { return expression.split("-"); };

    var syncTrix = function(target) {
      var proposalExpression = parseProposal(target.inputElement.id);
      var html = JSON.stringify(target.editor);
      meetingStorage.addOrUpdateUnit(proposalExpression[1], proposalExpression[2], html);
      meetingStorage.push();
      showHintForLocalChanges();
    };

    var syncProposal = function() {
      showHintForLocalChanges();
    };

    protocolSynchronizer.onSync(syncProposal);
    protocolSynchronizer.observe();

    trixSynchronizer.onSync(syncTrix);
    trixSynchronizer.observe();

    meetingStorage.pull();

    if(createdAt < meetingStorage.currentMeeting.revision) {
      meetingStorage.restore();
    }

    this.saveProtocol = function(target) {
      var form = target.parents("form");
      var payload = form.serializeArray();
      payload.push({ name: "form.buttons.save", value: saveButton.val() });
      var conflictValidator = function(data) {
        if(data.hasConflict) {
          showHintForConflictChanges();
        }
        return !data.hasConflict;
      };
      return this.request(form.attr("action"), { type: "POST", data: payload, validator: conflictValidator })
              .done(function(data) {
                if (data.redirectUrl !== undefined) {
                  meetingStorage.deleteCurrentMeeting();
                  window.location = data.redirectUrl;
                } else {
                  // we stay on the same site. allow re-submit.
                  $("#form-buttons-save").removeClass("submitting");
                }
             });
    };

    this.discardProtocol = function() { meetingStorage.deleteCurrentMeeting(); };

    this.events = [
      {
        method: "click",
        target: "#form-buttons-save",
        callback: this.saveProtocol
      },
      {
        method: "click",
        target: "#form-buttons-cancel",
        callback: this.discardProtocol,
        options: {
          prevent: false
        }
      }
    ];

    this.init();

    if(meetingStorage.currentMeeting.revision) {
      showHintForLocalChanges();
    }

  }

  function TrixController() {

    global.Controller.call(this);

    this.activateToolbar = function(toolbar) {
      $("trix-toolbar").removeClass("active");
      toolbar.addClass("active");
    };

    this.attachToolbar = function(target) {
      this.activateToolbar($("#" + target.attr("toolbar")));
    };

    this.events = [
      {
        method: "click",
        target: "trix-editor",
        callback: this.attachToolbar
      }
    ];

    this.init();

  }

  var trixController = new TrixController();

  function init() {

    var protocolController = new ProtocolController();

    var scrollspy = new global.Scrollspy({ selector: ".navigation" });

    var navigation = $(".protocol-navigation");

    var headings = new global.StickyHeading({ selector: "#opengever_meeting_protocol .protocol_title" });
    var labels = new global.StickyHeading({ selector: "#opengever_meeting_protocol .agenda_items label", fix: false, dependsOn: headings});
    var collapsible = new global.StickyHeading({ selector: "#opengever_meeting_protocol .collapsible", clone: false});

    scrollspy.onBeforeScroll(function(target, anchor) { scrollspy.options.offset = anchor.siblings("h2.clone").height() + 40; });

    collapsible.onSticky(function() {
      navigation.addClass("sticky");
      navigation.css("left", navigation.offset().left);
    });

    collapsible.onNoSticky(function() { navigation.css("left", "auto"); });

    headings.onNoSticky(function() {
      scrollspy.reset();
      navigation.removeClass("sticky");
    });

    headings.onSticky(function(heading) {
      navigation.addClass("sticky");
      scrollspy.expand($("#" + heading.node.attr("id") + "-anchor"));
      scrollspy.select($("#" + heading.node.attr("id") + "-anchor"));
    });

    headings.onCollision(function() { navigation.addClass("sticky"); });

    labels.onSticky(function(label) { scrollspy.select($("#" + label.node.attr("for") + "-anchor")); });

    labels.onCollision(function(fadingIn, fadingOut) { scrollspy.select($("#" + fadingOut.node.attr("for") + "-anchor")); });

    scrollspy.onScroll(function(target, anchor) {
      trixController.activateToolbar($("#" + anchor.attr("id") + "-toolbar"));
      if(target.hasClass("expandable")) {
        scrollspy.expand(target);
      }
    });


  }

  $(function() {
    if($("#opengever_meeting_protocol").length) {
      init();
    }
    if($(".template-add-membership, .template-opengever-meeting-proposal, .portaltype-opengever-meeting-proposal.template-edit").length) {
      var autocompleteSelects = new global.SelectAutocomplete();
    }
  });

}(window, jQuery));
