// function to call api to get list of job categories
// paht /api/v1/categories
const apiHost = "https://api.project-dam501.mse20hcm.top";
const getJobCategories = async () => {
  return $.ajax({
    url: `${apiHost}/api/v1/categories`,
    async: true,
    method: "GET",
  });
};

const getWordCloudSkills = async (category = "") => {
  return $.ajax({
    url: `${apiHost}/api/v1/resume/skills/wordcloud?category=${category}`,
    method: "GET",
    async: true,
    xhrFields: {
      responseType: "blob", // Expect a binary response (image file)
    },
    error: function (error) {
      console.log("getWordCloudSkills ~ error:", error);
    },
  });
};

const getTopCompaniesPostings = async () => {
  return $.ajax({
    url: `${apiHost}/api/v1/stats/top_companies/postings`,
    method: "GET",
    async: true,
  });
};

const getTopCategoriesPostings = async () => {
  return $.ajax({
    url: `${apiHost}/api/v1/stats/top_categories/resumes?top=10`,
    method: "GET",
    async: true,
  });
};

const getTopIndustriesCompanies = async () => {
  return $.ajax({
    url: `${apiHost}/api/v1/stats/top_companies/industry`,
    method: "GET",
    async: true,
  });
};

const getJobs = (limit = 10, offset = 0) => {
  let param = {
    limit: limit,
    offset: offset,
  };
  return $.ajax({
    url: `${apiHost}/api/v1/jobs?${$.param(param, true)}`,
    method: "GET",
    async: true,
    contentType: "application/json; charset=utf-8",
    dataType: "json",
  });
};

const getJobDetail = (id) => {
  return $.ajax({
    url: `${apiHost}/api/v1/jobs/${id}`,
    method: "GET",
    async: true,
    contentType: "application/json; charset=utf-8",
    dataType: "json",
  });
};

const updateStatistics = async () => {
  const category = $("#selectJobCategory").val();
  try {
    getWordCloudSkills(category).then((response) => {
      const blob = new Blob([response], { type: "image/png" });
      const url = URL.createObjectURL(blob);
      $("#wordCloudSkills").attr("src", url);
    });

    getTopCompaniesPostings().then((response) => {
      const data = response.data;

      const chartData = {
        labels: data.map((item) => item.company_name),
        datasets: [
          {
            label: "Num of postings",
            data: data.map((item) => item.count),
            backgroundColor: "rgba(98, 75, 192, 0.2)",
            borderColor: "rgba(98, 75, 192, 1)",
            borderWidth: 1,
          },
        ],
      };
      const config = {
        type: "bar",
        data: chartData,
        options: {
          indexAxis: "y",
          // Elements options apply to all of the options unless overridden in a dataset
          // In this case, we are setting the border of each horizontal bar to be 2px wide
          elements: {
            bar: {
              borderWidth: 2,
            },
          },
          responsive: true,
          plugins: {
            legend: {
              position: "right",
            },
            title: {
              display: true,
              text: "Top 10 Companies by Job Postings",
            },
          },
        },
      };

      const ctx = document.getElementById("topCompaniesPostingsChart");
      const myChart = new Chart(ctx, config);
    });
  } catch (error) {
    console.log("updateStatistics ~ error:", error);
  }
};

const showChartCategoriesPostings = async () => {
  try {
    getTopCategoriesPostings().then((response) => {
      const data = response.data;

      const chartData = {
        labels: data.map((item) => item.Category),
        datasets: [
          {
            label: "Num of postings",
            data: data.map((item) => item.count),
            backgroundColor: "rgba(99, 75, 191, 0.5)",
            borderColor: "rgba(99, 75, 191, 1)",
            borderWidth: 1,
          },
        ],
      };
      const config = {
        type: "bar",
        data: chartData,
        options: {
          indexAxis: "y",
          // Elements options apply to all of the options unless overridden in a dataset
          // In this case, we are setting the border of each horizontal bar to be 2px wide
          elements: {
            bar: {
              borderWidth: 2,
            },
          },
          responsive: true,
          plugins: {
            legend: {
              position: "right",
            },
            title: {
              display: true,
              text: "Top 10 Categories by Job Postings",
            },
          },
        },
      };

      const ctx = document.getElementById("topCategoriesPostingsChart");
      const myChart = new Chart(ctx, config);
    });
  } catch (error) {
    console.log("showChartCategoriesPostings ~ error:", error);
  }
};

// Function to shuffle the data array
function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
const showChartIndustriesCompanies = async () => {
  try {
    getTopIndustriesCompanies().then((response) => {
      let data = response.data;

      // random data sort
      data = shuffle([...data]);

      const chartData = {
        labels: data.map((item) => item.industry),
        datasets: [
          {
            label: "Num of companies",
            data: data.map((item) => item.count),
          },
        ],
      };
      const config = {
        type: "polarArea",
        data: chartData,
        options: {
          responsive: true,
          maintainAspectRatio: false,

          plugins: {
            legend: {
              position: "left",
            },
            title: {
              display: true,
              text: "Top 10 Industries by Companies",
            },
          },
        },
      };

      const ctx = document.getElementById("topIndustriesCompaniesChart");
      const myChart = new Chart(ctx, config);
    });
  } catch (error) {
    console.log("showChartIndustriesCompanies ~ error:", error);
  }
};
const viewJob = async (job_id) => {
  if (!job_id) return;
  const jobDetail = await getJobDetail(job_id);
  const job = jobDetail.data;
  console.log("viewJob ~ job:", job);
  $("#jobTitle").text("");
  $("#jobCompanyName").text("");
  $("#jobIndustry").text("");
  $("#jobDescription").text("");
  $("#jobTitle").text(job.title);
  $("#jobCompanyName").text(job.company_name);
  $("#jobIndustry").text(job.industry);
  $("#jobDescription").text(job.description);
  $("#jobDetailModal").modal("show");
};
$(function () {
  $.fn.dataTable.pipeline = function (opts) {
    let conf = $.extend(
      {
        pages: 3,
        url: "",
        data: null,
        method: "GET",
      },
      opts
    );
    let cacheLower = -1;
    let cacheUpper = null;
    let cacheLastRequest = null;
    let cacheLastJson = null;
    return (request, callback, settings) => {
      let ajax = false;
      let requestStart = request.start;
      let drawStart = request.start;
      let requestLength = request.length;
      let requestEnd = requestStart + requestLength;

      if (settings.clearCache) {
        ajax = true;
        settings.clearCache = false;
      } else if (
        cacheLower < 0 ||
        requestStart < cacheLower ||
        requestEnd > cacheUpper
      ) {
        ajax = true;
      } else if (
        JSON.stringify(request.order) !==
          JSON.stringify(cacheLastRequest.order) ||
        JSON.stringify(request.columns) !==
          JSON.stringify(cacheLastRequest.columns) ||
        JSON.stringify(request.search) !==
          JSON.stringify(cacheLastRequest.search)
      ) {
        ajax = true;
      }
      cacheLastRequest = $.extend(true, {}, request);

      if (ajax) {
        if (requestStart < cacheLower) {
          requestStart = requestStart - requestLength * (conf.pages - 1);

          if (requestStart < 0) {
            requestStart = 0;
          }
        }
        cacheLower = requestStart;
        cacheUpper = requestStart + requestLength * conf.pages;
        request.start = requestStart;
        request.length = requestLength * conf.pages;
        if (typeof conf.data === "function") {
          var d = conf.data(request);
          if (d) {
            $.extend(request, d);
          }
        } else if ($.isPlainObject(conf.data)) {
          $.extend(request, conf.data);
        }
        let json = {};
        let out = [];
        let total = 0;
        let offset = request.start;
        let limit = request.length;
        let data_counter = 1;
        getJobs(limit, offset).done((result) => {
          json.data = result.data;
          json.recordsTotal = result.total;
          json.recordsFiltered = result.total;
          cacheLastJson = $.extend(true, {}, json);
          if (json.data == null) {
            json.data = [];
          }
          if (cacheLower != drawStart) {
            json.data.splice(0, drawStart - cacheLower);
          }
          if (requestLength > 0) {
            json.data.splice(requestLength, json.data.length);
          }
          json.draw = request.draw;
          callback(json);
        });
      } else {
        json = $.extend(true, {}, cacheLastJson);
        json.draw = request.draw; // Update the echo for each response
        json.data.splice(0, requestStart - cacheLower);
        json.data.splice(requestLength, json.data.length);
        callback(json);
      }
    };
  };
  $.fn.dataTable.Api.register("clearPipeline()", function () {
    return this.iterator("table", function (settings) {
      settings.clearCache = true;
    });
  });
});

const initTableJobs = () => {
  $("#tableJobs").DataTable({
    lengthChange: true,
    pageLength: 10,
    paging: true,
    processing: true,
    destroy: true,
    serverSide: true,
    sort: false,
    searching: false,
    ajax: $.fn.dataTable.pipeline({
      pages: 5,
    }),
    columns: [
      {
        title: "Title",
        data: "title",
        render: function (data, type, row, meta) {
          return `<a href="javascript:void(0)" onClick="viewJob('${row.job_id}')">${data}</a>`;
        },
      },
      {
        title: "Company",
        data: "company_name",
      },
      {
        title: "Industry",
        data: "industry",
      },
    ],
  });
  $(".buttons-colvis").on("click", (e) => {
    $(".dt-button-collection").css({
      left: "-90px",
    });
  });
};
$(document).ready(async function () {
  await getJobCategories().then((response) => {
    const categories = response.data.map((item) => item);
    console.log("getJobCategories ~ categories:", categories);
    // append option
    $.each(categories, function (i, item) {
      $("#selectJobCategory").append(
        $("<option>", {
          value: item,
          text: item,
        })
      );
    });
  });

  showChartCategoriesPostings();

  showChartIndustriesCompanies();

  updateStatistics();

  initTableJobs();
});
