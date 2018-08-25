<?xml version="1.0" encoding="UTF-8"?>

<!--
  Copyright (c) 2018 SPARKL Limited. All Rights Reserved.
  Author: jacoby@sparkl.com

  Transforms a SPARKL XML document into a text tree view.
-->
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  exclude-result-prefixes="xsi">

  <xsl:output method="text"/>

  <!--
    Space separated list of tags to include.
  -->
  <xsl:param name="include"
    select="'folder,mix,service,field,notify,solicit,response,request,reply,consume'"/>

  <!--
    Document root.
  -->
  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>

  <!--
    Line of output for each element.
  -->
  <xsl:template match="*">
    <xsl:if test="contains($include, local-name())">
      <xsl:for-each select="ancestor-or-self::*">
        <xsl:call-template name="indent"/>
      </xsl:for-each>

      <xsl:apply-templates select="." mode="prefix"/>
      <xsl:value-of select="@name"/>
      <xsl:text>&#x0a;</xsl:text>

      <xsl:apply-templates/>
    </xsl:if>
  </xsl:template>

  <!--
    Content to ignore.
  -->
  <xsl:template match="text()"/>

  <!--
    Indents by depth.

    The position() function refers to the ancestor axis where
    1 = root and last() is the leaf whose line we're rendering.
  -->
  <xsl:template name="indent">
    <xsl:choose>

      <!--
        Root element has no indent
      -->
      <xsl:when test="position()=1"/>

      <!--
        Intermediate ancestors between root and leaf have a
        vertical bar continuation if they have following sibling(s).
       -->
      <xsl:when test="position()!=last()">
        <xsl:choose>
          <xsl:when test="following-sibling::*[contains($include,local-name())]">
            <xsl:text>│   </xsl:text>
          </xsl:when>

          <xsl:otherwise>
            <xsl:text>    </xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <!--
        Leaf has pointer.
      -->
      <xsl:when test="position()=last()">
        <xsl:choose>
          <xsl:when test="following-sibling::*[contains($include,local-name())]">
            <xsl:text>├── </xsl:text>
          </xsl:when>

          <xsl:otherwise>
            <xsl:text>└── </xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
    Prefixes, none by default.
  -->
  <xsl:template match="mix" mode="prefix">
    <xsl:text>µ </xsl:text>
  </xsl:template>

  <xsl:template match="field" mode="prefix">
    <xsl:text>ƒ </xsl:text>
  </xsl:template>

  <xsl:template match="service" mode="prefix">
    <xsl:text>▒ </xsl:text>
  </xsl:template>

  <xsl:template match="notify|solicit" mode="prefix">
    <xsl:text>» </xsl:text>
  </xsl:template>

  <xsl:template match="request|consume" mode="prefix">
    <xsl:text>« </xsl:text>
  </xsl:template>

  <xsl:template match="*" mode="prefix"/>

</xsl:stylesheet>
