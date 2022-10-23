/** @odoo-module **/

import AbstractFieldOwl from "web.AbstractFieldOwl";
import fieldRegistryOwl from "web.field_registry_owl";

const { useState, onWillUpdateProps, onMounted, useRef } = owl.hooks;

export default class DepartmentOrgChart extends AbstractFieldOwl {
  constructor(...args) {
    super(...args);
  }

  setup() {
    super.setup();
    console.log("THIS: ", this);
    this.chart = null;

    this.state = useState({
      data: JSON.parse(this.value),
    });

    onWillUpdateProps(async (nextProps) => {
      this._renderD3OrgChart();
    });

    onMounted(() => {
      this._renderD3OrgChart();
    });
  }

  _renderD3OrgChart() {
    const dataFlattened = this.state.data;
    this.chart = new d3.OrgChart()
      .container(".chart-container")
      .data(dataFlattened)
      .rootMargin(100)
      .nodeWidth((d) => 210)
      .nodeHeight((d) => 160)
      .childrenMargin((d) => 130)
      .compactMarginBetween((d) => 75)
      .compactMarginPair((d) => 80)
      .initialZoom(0.6)
      .onNodeClick((d) => {
        console.log(d + " node clicked");
      })
      .nodeContent(function (d, i, arr, state) {
        const colors = [
          "#6E6B6F",
          "#18A8B6",
          "#F45754",
          "#96C62C",
          "#BD7E16",
          "#802F74",
        ];
        const color = colors[d.depth % colors.length];
        const imageDim = 80;
        const lightCircleDim = 95;
        const outsideCircleDim = 110;
        const image = `
            <div style="background-color:${color};position:absolute;margin-top:-${
          outsideCircleDim / 2
        }px;margin-left:${
          d.width / 2 - outsideCircleDim / 2
        }px;border-radius:100px;width:${outsideCircleDim}px;height:${outsideCircleDim}px;"></div>
            <div style="background-color:#ffffff;position:absolute;margin-top:-${
              lightCircleDim / 2
            }px;margin-left:${
          d.width / 2 - lightCircleDim / 2
        }px;border-radius:100px;width:${lightCircleDim}px;height:${lightCircleDim}px;"></div>
            <img src="${
              d.data.imageUrl
            }" style="position:absolute;margin-top:-${
          imageDim / 2
        }px;margin-left:${
          d.width / 2 - imageDim / 2
        }px;border-radius:100px;width:${imageDim}px;height:${imageDim}px;" />
          `;
        const positionName = `
          <div style="background-color:#F0EDEF;height:45px;text-align:center;padding-top:10px;color:#424142;font-size:16px">
              ${d.data.positionName} 
          </div>
        `;
        return `
                <div style="background-color:white; position:absolute;width:${
                  d.width
                }px;height:${d.height}px;">

                   ${d.data.imageUrl ? image : ""}

                   <div class="card" style="top:${
                     outsideCircleDim / 2 + 10
                   }px;position:absolute;height:95px;width:${d.width}px;background-color:#3AB6E3;">
                      <div style="background-color:${color};height:50px;text-align:center;padding-top:10px;color:#ffffff;font-weight:bold;font-size:16px">
                          ${d.data.name} 
                      </div>
                      ${d.data.positionName ? positionName : ""}
                   </div>
               </div>
            `;
      })
      .render()
      .expandAll();
    console.log(this.chart);
  }
  _downloadOrgImg() {
    this.chart.exportImg({ full: true, scale: 5 });
  }
}

DepartmentOrgChart.template = "DepartmentOrgChart";
DepartmentOrgChart.components = {};

fieldRegistryOwl.add("department_org_chart", DepartmentOrgChart);
