(function () {
  "use strict";

  var app = document.getElementById("activity-availability-app");
  if (!app) return;

  var statusNode = app.querySelector("[data-activity-calendar-status]");
  var errorNode = app.querySelector("[data-activity-calendar-error]");
  var monthsNode = app.querySelector("[data-activity-calendar-months]");
  var calendarSource = app.dataset.calendarSource;
  var trackedKeywords = ["\u71b1\u6c23\u7403", "\u96f2\u6735", "\u5305\u5834"];
  var weekdays = ["一", "二", "三", "四", "五", "六", "日"];

  function unfoldIcs(text) {
    return text.replace(/\r\n/g, "\n").replace(/\n[\t ]/g, "");
  }

  function parseProperties(block) {
    var properties = {};
    block.split("\n").forEach(function (line) {
      var separator = line.indexOf(":");
      if (separator === -1) return;
      var keyPart = line.slice(0, separator);
      var key = keyPart.split(";")[0];
      if (!properties[key]) {
        properties[key] = { keyPart: keyPart, value: line.slice(separator + 1) };
      }
    });
    return properties;
  }

  function parseIcsDate(property) {
    if (!property) return null;
    var value = property.value.trim();
    if (property.keyPart.indexOf("VALUE=DATE") !== -1 && /^\d{8}$/.test(value)) {
      return new Date(
        Number(value.slice(0, 4)),
        Number(value.slice(4, 6)) - 1,
        Number(value.slice(6, 8)),
        0,
        0,
        0,
        0
      );
    }
    if (/^\d{8}T\d{6}Z?$/.test(value)) {
      var datePart = value.slice(0, 8);
      var timePart = value.slice(9, 15);
      return new Date(
        datePart.slice(0, 4) + "-" +
        datePart.slice(4, 6) + "-" +
        datePart.slice(6, 8) + "T" +
        timePart.slice(0, 2) + ":" +
        timePart.slice(2, 4) + ":" +
        timePart.slice(4, 6) +
        (value.endsWith("Z") ? "Z" : "")
      );
    }
    var timestamp = Date.parse(value);
    return Number.isNaN(timestamp) ? null : new Date(timestamp);
  }

  function isTrackedEvent(summary, description) {
    var title = (summary || "").replace(/^\s+/, "");
    if (title.charAt(0) === "?" || title.charAt(0) === "？") return false;
    var searchable = title + "\n" + (description || "");
    return trackedKeywords.some(function (keyword) {
      return searchable.indexOf(keyword) !== -1;
    });
  }

  function parseEvents(icsText) {
    var parts = unfoldIcs(icsText).split(/BEGIN:VEVENT\r?\n/);
    var events = [];
    for (var index = 1; index < parts.length; index += 1) {
      var properties = parseProperties(parts[index].split(/END:VEVENT/)[0]);
      var summary = properties.SUMMARY ? properties.SUMMARY.value : "";
      var description = properties.DESCRIPTION ? properties.DESCRIPTION.value : "";
      if (!isTrackedEvent(summary, description)) continue;

      var start = parseIcsDate(properties.DTSTART);
      var end = parseIcsDate(properties.DTEND);
      if (!start) continue;
      if (!end) {
        end = new Date(start.getTime());
        end.setDate(end.getDate() + 1);
      }
      events.push({ start: start, end: end });
    }
    return events;
  }

  function overlapsDay(event, year, month, day) {
    var dayStart = new Date(year, month, day, 0, 0, 0, 0);
    var dayEnd = new Date(year, month, day + 1, 0, 0, 0, 0);
    return event.end > dayStart && event.start < dayEnd;
  }

  function isBooked(events, year, month, day) {
    return events.some(function (event) {
      return overlapsDay(event, year, month, day);
    });
  }

  function sameDate(left, right) {
    return left.getFullYear() === right.getFullYear() &&
      left.getMonth() === right.getMonth() &&
      left.getDate() === right.getDate();
  }

  function monthCells(year, month) {
    var cells = [];
    var firstDay = new Date(year, month, 1);
    var leading = (firstDay.getDay() + 6) % 7;
    var daysInMonth = new Date(year, month + 1, 0).getDate();
    for (var pad = 0; pad < leading; pad += 1) cells.push(null);
    for (var day = 1; day <= daysInMonth; day += 1) cells.push(day);
    while (cells.length % 7) cells.push(null);
    return cells;
  }

  function renderMonth(events, year, month, today) {
    var article = document.createElement("article");
    article.className = "activity-calendar-month card";

    var heading = document.createElement("h3");
    heading.textContent = year + " 年 " + (month + 1) + " 月";
    article.appendChild(heading);

    var grid = document.createElement("div");
    grid.className = "activity-calendar-grid";
    grid.setAttribute("role", "grid");
    grid.setAttribute("aria-label", heading.textContent + "活動場地檔期");

    weekdays.forEach(function (weekday) {
      var head = document.createElement("div");
      head.className = "activity-calendar-weekday";
      head.textContent = weekday;
      head.setAttribute("role", "columnheader");
      grid.appendChild(head);
    });

    monthCells(year, month).forEach(function (day) {
      var cell = document.createElement("div");
      if (!day) {
        cell.className = "activity-calendar-day is-empty";
        cell.setAttribute("aria-hidden", "true");
        grid.appendChild(cell);
        return;
      }

      var date = new Date(year, month, day, 0, 0, 0, 0);
      var past = date < today;
      var booked = !past && isBooked(events, year, month, day);
      var state = past ? "已過日期" : (booked ? "已預約" : "可預約");
      var stateClass = past ? "is-past" : (booked ? "is-booked" : "is-available");

      cell.className = "activity-calendar-day " + stateClass;
      if (sameDate(date, today)) cell.className += " is-today";
      cell.setAttribute("role", "gridcell");
      cell.setAttribute("aria-label", (month + 1) + " 月 " + day + " 日，" + state);

      var number = document.createElement("span");
      number.className = "activity-calendar-day-number";
      number.textContent = day;
      cell.appendChild(number);

      var label = document.createElement("span");
      label.className = "activity-calendar-day-state";
      label.textContent = state;
      cell.appendChild(label);
      grid.appendChild(cell);
    });

    article.appendChild(grid);
    return article;
  }

  function render(events) {
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var fragment = document.createDocumentFragment();
    for (var offset = 0; offset < 6; offset += 1) {
      var monthDate = new Date(now.getFullYear(), now.getMonth() + offset, 1);
      fragment.appendChild(renderMonth(events, monthDate.getFullYear(), monthDate.getMonth(), today));
    }
    monthsNode.replaceChildren(fragment);
    statusNode.textContent = "檔期已同步完成；最後更新：" +
      new Intl.DateTimeFormat("zh-TW", { dateStyle: "medium", timeStyle: "short" }).format(new Date());
  }

  async function loadAvailability() {
    try {
      var separator = calendarSource.indexOf("?") === -1 ? "?" : "&";
      var response = await fetch(calendarSource + separator + "_ts=" + Date.now(), { cache: "no-store", mode: "cors" });
      if (!response.ok) throw new Error("HTTP " + response.status);
      render(parseEvents(await response.text()));
    } catch (error) {
      statusNode.textContent = "";
      errorNode.hidden = false;
      errorNode.textContent = "目前無法同步活動檔期，請稍後重新整理，或直接加 Line 詢問日期。";
    }
  }

  loadAvailability();
})();
