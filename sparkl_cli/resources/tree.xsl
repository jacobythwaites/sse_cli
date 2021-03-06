<?xml version="1.0" encoding="UTF-8"?>

<!--
  Copyright 2018 SPARKL Limited

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  Author: jacoby@sparkl.com

  Transforms a SPARKL XML document into a text tree view.
-->
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  exclude-result-prefixes="xsi">

  <xsl:output method="text" encoding="UTF-8"/>

  <!--
    Flag to control detail on the line for each entry.
  -->
  <xsl:param name="detail"
    select="false()"/>

 <!--
    Space separated list of tags to include.
  -->
  <xsl:param name="tags">
    folder,mix,service,field,notify,solicit,
    response,request,reply,consume,prop
  </xsl:param>

  <!--
    See https://www.w3schools.com/charsets/ref_utf_box.asp
    Note that the Windows console must be set to UTF8 using
    the chcp 65001 command.
  -->
  <xsl:variable name="outer-vertical">&#x2502;   </xsl:variable>
  <xsl:variable name="non-terminal">&#x251C;&#x2500;&#x2500; </xsl:variable>
  <xsl:variable name="non-terminal-mix">&#x255E;&#x2550;&#x2550; </xsl:variable>
  <xsl:variable name="terminal">&#x2514;&#x2500;&#x2500; </xsl:variable>
  <xsl:variable name="terminal-mix">&#x2558;&#x2550;&#x2550; </xsl:variable>
  <xsl:variable name="mix-prefix">&#x03BC;  </xsl:variable>
  <xsl:variable name="field-prefix">&#x0192;  </xsl:variable>
  <xsl:variable name="service-prefix">&#x2592;  </xsl:variable>
  <xsl:variable name="notify-prefix">&gt;&gt; </xsl:variable>
  <xsl:variable name="solicit-prefix">&gt;&gt; </xsl:variable>
  <xsl:variable name="response-prefix">&lt;&lt; </xsl:variable>
  <xsl:variable name="request-prefix">&lt;  </xsl:variable>
  <xsl:variable name="request-reply-prefix">&gt;  </xsl:variable>
  <xsl:variable name="consume-prefix">&lt;&lt; </xsl:variable>
  <xsl:variable name="consume-reply-prefix">&gt;&gt; </xsl:variable>
  <xsl:variable name="prop-prefix">&#x25CB;  </xsl:variable>
  <xsl:variable name="content-indicator"> &#x00B6;</xsl:variable>

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
    <xsl:if test="contains($tags, local-name())">
      <xsl:for-each select="ancestor-or-self::*">
        <xsl:call-template name="indent"/>
      </xsl:for-each>

      <xsl:apply-templates select="." mode="leaf"/>

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
          <xsl:when test="following-sibling::*[contains($tags,local-name())]">
            <xsl:value-of select="$outer-vertical"/>
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
          <xsl:when test="following-sibling::*[contains($tags,local-name())]">
            <xsl:choose>
              <xsl:when test="local-name()='mix'">
                <xsl:value-of select="$non-terminal-mix"/>
              </xsl:when>

              <xsl:otherwise>
                <xsl:value-of select="$non-terminal"/>
              </xsl:otherwise>
            </xsl:choose>

          </xsl:when>

          <xsl:otherwise>
            <xsl:choose>
              <xsl:when test="local-name()='mix'">
                <xsl:value-of select="$terminal-mix"/>
              </xsl:when>

              <xsl:otherwise>
                <xsl:value-of select="$terminal"/>
              </xsl:otherwise>
            </xsl:choose>

          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
    Leaf text after indent per subject type.
  -->
  <xsl:template match="folder" mode="leaf">
    <xsl:value-of select="@name"/>

    <xsl:call-template name="grants"/>
  </xsl:template>

  <xsl:template match="mix" mode="leaf">
    <xsl:value-of select="$mix-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="grants"/>
  </xsl:template>

  <xsl:template match="field" mode="leaf">
    <xsl:value-of select="$field-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:if test="$detail and @type">
      <xsl:text>:</xsl:text>
      <xsl:value-of select="@type"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="service" mode="leaf">
    <xsl:value-of select="$service-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:if test="$detail">
      <xsl:if test="@provision">
        <xsl:text>:</xsl:text>
        <xsl:value-of select="@provision"/>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <xsl:template match="notify" mode="leaf">
    <xsl:value-of select="$notify-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="service_ref"/>
    <xsl:call-template name="field_refs"/>
  </xsl:template>

  <xsl:template match="solicit" mode="leaf">
    <xsl:value-of select="$solicit-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="service_ref"/>
    <xsl:call-template name="field_refs"/>
  </xsl:template>

  <xsl:template match="request" mode="leaf">
    <xsl:value-of select="$request-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="service_ref"/>
    <xsl:call-template name="field_refs"/>
  </xsl:template>

  <xsl:template match="consume" mode="leaf">
    <xsl:value-of select="$consume-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="service_ref"/>
    <xsl:call-template name="field_refs"/>
  </xsl:template>

  <xsl:template match="response" mode="leaf">
    <xsl:value-of select="$response-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="field_refs"/>
  </xsl:template>

  <xsl:template match="request/reply" mode="leaf">
    <xsl:value-of select="$request-reply-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="field_refs"/>
  </xsl:template>

  <xsl:template match="consume/reply" mode="leaf">
    <xsl:value-of select="$consume-reply-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="field_refs"/>
  </xsl:template>

  <xsl:template match="prop" mode="leaf">
    <xsl:value-of select="$prop-prefix"/>
    <xsl:value-of select="@name"/>

    <xsl:call-template name="prop-detail"/>
  </xsl:template>

  <xsl:template name="service_ref">
    <xsl:if test="$detail and @service">
      <xsl:text>:</xsl:text>
      <xsl:value-of select="@service"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="field_refs">
    <xsl:if test="$detail">
      <xsl:text> </xsl:text>
      <xsl:value-of select="@fields"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="grants">
    <xsl:if test="$detail and grant">
      <xsl:for-each select="grant">
        <xsl:text> </xsl:text>
        <xsl:value-of select="@to"/>
        <xsl:text>:</xsl:text>
        <xsl:value-of select="@permission"/>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>

  <xsl:template name="prop-detail">
    <xsl:if test="$detail">
      <xsl:for-each select="@*">
        <xsl:if test="local-name()!='name'">
          <xsl:text> </xsl:text>
          <xsl:value-of select="local-name()"/>
          <xsl:text>=</xsl:text>
          <xsl:value-of select="."/>
        </xsl:if>
      </xsl:for-each>

      <xsl:if test="text()">
        <xsl:value-of select="$content-indicator"/>
      </xsl:if>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
