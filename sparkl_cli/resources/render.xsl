<?xml version="1.0" encoding="UTF-8"?>

<!--
  Copyright (c) 2018 SPARKL Limited. All Rights Reserved.
  Author: jacoby@sparkl.com

  Transforms a SPARKL XML document into HTML.
-->
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xi="http://www.w3.org/2001/XInclude"
  exclude-result-prefixes="xsi xi">

  <xsl:output method="html" indent="yes"/>

  <!--
    Generates an HTML document.
  -->
  <xsl:template match="/">
    <html>
      <head>
        <title>
          <xsl:value-of select="*/@name"/>
        </title>
        <xsl:call-template name="css"/>
      </head>
      <body>
        <xsl:apply-templates/>
        <xsl:call-template name="js"/>
      </body>
    </html>
  </xsl:template>

  <!--
    Folder.
  -->
  <xsl:template match="folder">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:call-template name="open-close-header">
        <xsl:with-param name="state" select="'opened'"/>
      </xsl:call-template>
      <xsl:call-template name="folder-content"/>
    </xsl:copy>
  </xsl:template>

  <!--
    Mix.
  -->
  <xsl:template match="mix">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:call-template name="open-close-header">
        <xsl:with-param name="state" select="'opened'"/>
      </xsl:call-template>
      <xsl:call-template name="folder-content"/>
    </xsl:copy>
  </xsl:template>

  <!--
    Folder contents.
  -->
  <xsl:template name="folder-content">
    <content>
      <xsl:call-template name="props"/>

      <xsl:if test="service">
        <services>
          <xsl:apply-templates select="service"/>
        </services>
      </xsl:if>

      <xsl:if test="field">
        <fields>
          <xsl:apply-templates select="field"/>
        </fields>
      </xsl:if>

      <xsl:if test="notify|solicit|request|consume">
        <operations>
          <xsl:apply-templates
            select="notify|solicit|request|consume"/>
        </operations>
      </xsl:if>

      <xsl:if test="folder|mix">
        <folders>
          <xsl:apply-templates select="folder|mix"/>
        </folders>
      </xsl:if>
    </content>
  </xsl:template>

  <!--
    Service.
  -->
  <xsl:template match="service">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:call-template name="open-close-header"/>
      <content>
        <xsl:call-template name="attr-table"/>
        <xsl:call-template name="props"/>
      </content>
    </xsl:copy>
  </xsl:template>

  <!--
    Field.
  -->
  <xsl:template match="field">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:call-template name="open-close-header"/>
      <content>
        <xsl:call-template name="attr-table"/>
        <xsl:call-template name="props"/>
      </content>
    </xsl:copy>
  </xsl:template>

  <!--
    Prop.
  -->
  <xsl:template match="prop">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:call-template name="open-close-header">
        <xsl:with-param name="show-icon-if"
          select="@*[not(local-name()='name')]|text()"/>
      </xsl:call-template>
      <content>
        <xsl:call-template name="attr-table"/>
        <xsl:apply-templates/>
      </content>
    </xsl:copy>
  </xsl:template>

  <!--
    Prop text content.
  -->
  <xsl:template match="prop/text()">
    <pre>
      <xsl:value-of select="."/>
    </pre>
  </xsl:template>

  <!--
    Notify.
  -->
  <xsl:template match="notify">
    <table class="operation">
      <tr class="notify">
        <td class="set">
          <notify>
            <xsl:call-template name="set"/>
          </notify>
        </td>
        <td class="fields">
          <xsl:apply-templates select="@fields"/>
        </td>
      </tr>
    </table>
  </xsl:template>

  <!--
    Solicit/Response.
  -->
  <xsl:template match="solicit">
    <table class="operation">
      <tr class="solicit">
        <td class="set">
          <solicit>
            <xsl:call-template name="set"/>
          </solicit>
        </td>
        <td class="fields">
          <xsl:apply-templates select="@fields"/>
        </td>
      </tr>
      <xsl:for-each select="response">
        <tr class="response">
          <td class="set">
            <response>
              <xsl:call-template name="set"/>
            </response>
          </td>
          <td class="fields">
            <xsl:apply-templates select="@fields"/>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <!--
    Request/Reply.
  -->
  <xsl:template match="request">
    <table class="operation">
      <tr class="request">
        <td class="set">
          <request>
            <xsl:call-template name="set"/>
          </request>
        </td>
        <td class="fields">
          <xsl:apply-templates select="@fields"/>
        </td>
      </tr>
      <xsl:for-each select="reply">
        <tr class="reply">
          <td class="set">
            <reply>
              <xsl:call-template name="set"/>
            </reply>
          </td>
          <td class="fields">
            <xsl:apply-templates select="@fields"/>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <!--
    Consume[/Reply].
  -->
  <xsl:template match="consume">
    <table class="operation">
      <tr class="consume">
        <td class="set">
          <consume>
            <xsl:call-template name="set"/>
          </consume>
        </td>
        <td class="fields">
          <xsl:apply-templates select="@fields"/>
        </td>
      </tr>
      <xsl:for-each select="reply">
        <tr class="reply">
          <td class="set">
            <reply>
              <xsl:call-template name="set"/>
            </reply>
          </td>
          <td class="fields">
            <xsl:apply-templates select="@fields"/>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <!--
    Output fields.
  -->
  <xsl:template
    match="notify/@fields|solicit/@fields|reply/@fields">
    <xsl:call-template name="fields">
      <xsl:with-param name="string" select="."/>
    </xsl:call-template>
  </xsl:template>

  <!--
    Input fields.
  -->
  <xsl:template
    match="response/@fields|request/@fields|consume/@fields">
    <xsl:call-template name="fields">
      <xsl:with-param name="string" select="."/>
    </xsl:call-template>
  </xsl:template>

  <!--
    Attributes are copied.
  -->
  <xsl:template match="@*">
    <xsl:copy-of select="."/>
  </xsl:template>

  <!--
    Everything else is ignored.
  -->
  <xsl:template match="node()|@*"/>

  <!--
    The input or output set of an operation, excluding fields.
  -->
  <xsl:template name="set">
    <xsl:copy-of select="@*"/>
    <xsl:call-template name="open-close-header">
      <xsl:with-param name="show-icon-if"
        select="@*[not(local-name()='name')][not(local-name()='fields')]|*"/>
    </xsl:call-template>
    <content>
      <xsl:call-template name="attr-table">
        <xsl:with-param name="omit" select="'name fields'"/>
      </xsl:call-template>
      <xsl:call-template name="props"/>
    </content>
  </xsl:template>

  <!--
    Open-close action header with state 'opened' or 'closed'.
    This must come *before* any content except attributes.
  -->
  <xsl:template name="open-close-header">
    <xsl:param name="show-icon-if" select="@*[not(local-name()='name')]|*"/>
    <xsl:param name="state" select="'closed'"/>
    <xsl:attribute name="class">
      <xsl:value-of select="$state"/>
    </xsl:attribute>
    <xsl:attribute name="action">open-close</xsl:attribute>
    <header>
      <xsl:if test="$show-icon-if">
        <span class="icon open-close"/>
      </xsl:if>
      <span class="name">
        <xsl:value-of select="@name"/>
      </span>
    </header>
  </xsl:template>

  <!--
    Attributes table.
    By default, omits the 'name=' attribute.
    Supply the 'omit' param to change.
  -->
  <xsl:template name="attr-table">
    <xsl:param name="omit" select="'name'"/>
    <xsl:variable name="spaced-omit"
      select="concat(' ',$omit,' ')"/>
    <table class="attributes">
      <xsl:for-each select="@*">
        <xsl:variable name="spaced-name"
          select="concat(' ',local-name(),' ')"/>
        <xsl:if test="not(contains($spaced-omit,$spaced-name))">
          <tr>
            <td class="attr-name">
              <xsl:value-of select="local-name()"/>
            </td>
            <td class="attr-value">
              <xsl:value-of select="."/>
            </td>
          </tr>
        </xsl:if>
      </xsl:for-each>
    </table>
  </xsl:template>

  <!--
    Props, if present.
  -->
  <xsl:template name="props">
    <xsl:if test="prop">
      <props>
        <xsl:apply-templates select="prop"/>
      </props>
    </xsl:if>
  </xsl:template>

  <!--
    Fields, input or output, space separated.
  -->
  <xsl:template name="fields">
    <xsl:param name="string"/>
    <xsl:choose>
      <xsl:when test="contains($string,' ')">
        <xsl:call-template name="field">
          <xsl:with-param
            name="string"
            select="substring-before($string,' ')"/>
        </xsl:call-template>
        <xsl:call-template name="fields">
          <xsl:with-param
            name="string"
            select="substring-after($string,' ')"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="field">
          <xsl:with-param
            name="string"
            select="$string"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
    Field, input or output.
  -->
  <xsl:template name="field">
    <xsl:param name="string"/>
    <div>
      <span class="icon"/>
      <span class="label">
        <xsl:value-of select="$string"/>
      </span>
    </div>
  </xsl:template>


  <!--
    Javascript inline.
  -->
  <xsl:template name="js">
    <script>
      <xi:include href="render.js" parse="text"/>
    </script>
  </xsl:template>

  <!--
    CSS stylesheet inline.
  -->
  <xsl:template name="css">
    <style>
      <xi:include href="render.css" parse="text"/>
    </style>
  </xsl:template>

</xsl:stylesheet>
