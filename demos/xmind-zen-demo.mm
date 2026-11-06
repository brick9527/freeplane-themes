<map version="freeplane 1.9.8">
<!--To view this file, download free mind mapping software Freeplane from https://www.freeplane.org -->
<node TEXT="年度产品计划" LOCALIZED_STYLE_REF="AutomaticLayout.level.root" FOLDED="false" ID="ID_1500000001" CREATED="1730000000000" MODIFIED="1730000000000">

<hook NAME="accessories/plugins/AutomaticLayout.properties" VALUE="ALL"/>
<font BOLD="true"/>
<hook NAME="MapStyle" background="#ffffff">
    <properties auto_compact_layout="true" show_icon_for_attributes="true" show_note_icons="true" show_icons="BESIDE_NODES" fit_to_viewport="false" edgeColorConfiguration="#4c7fd1ff,#df684cff,#6fae5aff,#e8a33dff,#6c5b9eff,#2a9d8fff,#e06c9fff,#55707fff"/>

<map_styles>
<stylenode LOCALIZED_TEXT="styles.root_node" STYLE="oval" UNIFORM_SHAPE="true" VGAP_QUANTITY="34 pt">
<font SIZE="24"/>
<stylenode LOCALIZED_TEXT="styles.predefined" POSITION="right">
<stylenode LOCALIZED_TEXT="default" ID="ID_1500000002" VGAP_QUANTITY="12 pt" ICON_SIZE="15 pt" COLOR="#111827" STYLE="fork" FORMAT_AS_HYPERLINK="false">
<arrowlink SHAPE="CUBIC_CURVE" COLOR="#4c7fd1" WIDTH="2" TRANSPARENCY="200" DASH="" FONT_SIZE="9" FONT_FAMILY="SansSerif" DESTINATION="ID_1500000002" ENDARROW="DEFAULT"/>
<font NAME="SansSerif" SIZE="13" BOLD="false" ITALIC="false" STRIKETHROUGH="false"/>
<edge STYLE="bezier" COLOR="#4c7fd1" WIDTH="3" DASH="SOLID"/>
<richcontent CONTENT-TYPE="plain/auto" TYPE="DETAILS"/>
<richcontent TYPE="NOTE" CONTENT-TYPE="plain/auto"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.details" COLOR="#6b7280">
<font SIZE="10" ITALIC="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.attributes" COLOR="#6b7280">
<font SIZE="10"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.note" COLOR="#7a5b00" BACKGROUND_COLOR="#fff8e1" TEXT_ALIGN="LEFT">
<icon BUILTIN="clock2"/>
<font SIZE="10"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.selection" COLOR="#ffffff" BACKGROUND_COLOR="#4c7fd1" BORDER_COLOR_LIKE_EDGE="false" BORDER_COLOR="#4c7fd1"/>
<stylenode LOCALIZED_TEXT="defaultstyle.floating" COLOR="#111827">
<edge STYLE="hide_edge"/>
<cloud COLOR="#f4f6fa" SHAPE="ROUND_RECT"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.user-defined" POSITION="right">
<stylenode LOCALIZED_TEXT="styles.important" ID="ID_1500000003" COLOR="#ffffff" BACKGROUND_COLOR="#df684c" BORDER_COLOR_LIKE_EDGE="false" BORDER_COLOR="#df684c" BORDER_WIDTH="0 pt" STYLE="bubble" SHAPE_HORIZONTAL_MARGIN="9 pt" SHAPE_VERTICAL_MARGIN="4 pt" TEXT_ALIGN="LEFT">
<icon BUILTIN="yes"/>
<arrowlink COLOR="#df684c" DESTINATION="ID_1500000003"/>
<font SIZE="12" BOLD="true"/>
</stylenode>
<stylenode TEXT="Tag" COLOR="#ffffff" BACKGROUND_COLOR="#284f71" BORDER_COLOR_LIKE_EDGE="false" BORDER_COLOR="#284f71" BORDER_WIDTH="0 pt" STYLE="bubble" SHAPE_HORIZONTAL_MARGIN="9 pt" SHAPE_VERTICAL_MARGIN="4 pt" MIN_WIDTH="0 pt" MAX_WIDTH="8 cm" TEXT_ALIGN="LEFT">
<font SIZE="11" BOLD="true"/>
</stylenode>
<stylenode TEXT="Accent" COLOR="#df684c">
<font SIZE="13" BOLD="true"/>
</stylenode>
<stylenode TEXT="Muted" COLOR="#8b95a3">
<font SIZE="12" ITALIC="true"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.AutomaticLayout" POSITION="right">
<stylenode LOCALIZED_TEXT="AutomaticLayout.level.root" COLOR="#ffffff" BACKGROUND_COLOR="#284f71" STYLE="bubble" SHAPE_HORIZONTAL_MARGIN="22 pt" COMMON_HGAP_QUANTITY="38 pt" VGAP_QUANTITY="24 pt" SHAPE_VERTICAL_MARGIN="12 pt" BORDER_WIDTH_LIKE_EDGE="false" BORDER_WIDTH="0 pt" BORDER_COLOR_LIKE_EDGE="false" BORDER_COLOR="#284f71" BORDER_DASH_LIKE_EDGE="false" BORDER_DASH="SOLID">
<font NAME="SansSerif" SIZE="20" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,1" COLOR="#111827">
<font SIZE="16" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,2" COLOR="#1f2937">
<font SIZE="13"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,3" COLOR="#374151">
<font SIZE="12"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,4" COLOR="#4b5563">
<font SIZE="11"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,5" COLOR="#6b7280">
<font SIZE="11"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,6" COLOR="#6b7280">
<font SIZE="10"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,7" COLOR="#6b7280">
<font SIZE="10"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,8" COLOR="#6b7280">
<font SIZE="10"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,9" COLOR="#6b7280">
<font SIZE="10"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,10" COLOR="#6b7280">
<font SIZE="10"/>
</stylenode>
</stylenode>
</stylenode>
</map_styles>
</hook>
<hook NAME="AutomaticEdgeColor" COUNTER="0" RULE="ON_BRANCH_CREATION"/>
  <node TEXT="产品规划" LOCALIZED_STYLE_REF="styles.important" ID="ID_1700000001"><edge COLOR="#df684c"/>    <node TEXT="竞品分析" ID="ID_1700000002"><edge COLOR="#df684c"/>    </node>
    <node TEXT="版本路线图" ID="ID_1700000003"><edge COLOR="#df684c"/>    </node>
  </node>
  <node TEXT="技术方案" STYLE_REF="Tag" ID="ID_1700000004"><edge COLOR="#4c7fd1"/>    <node TEXT="架构升级" ID="ID_1700000005"><edge COLOR="#4c7fd1"/>    </node>
    <node TEXT="性能优化" ID="ID_1700000006"><edge COLOR="#4c7fd1"/>    </node>
  </node>
  <node TEXT="市场推广" ID="ID_1700000007"><edge COLOR="#6fae5a"/>    <node TEXT="内容营销" ID="ID_1700000008"><edge COLOR="#6fae5a"/>    </node>
    <node TEXT="渠道投放" ID="ID_1700000009"><edge COLOR="#6fae5a"/>    </node>
  </node>
  <node TEXT="团队安排" ID="ID_1700000010"><edge COLOR="#e8a33d"/>    <node TEXT="招聘 3 人" ID="ID_1700000011"><edge COLOR="#e8a33d"/>    </node>
    <node TEXT="培训" ID="ID_1700000012"><edge COLOR="#e8a33d"/>    </node>
  </node>
</node>
</map>
