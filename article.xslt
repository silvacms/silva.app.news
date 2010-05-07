<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
  exclude-result-prefixes="doc silva silva-content silva-extra"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:doc="http://infrae.com/namespace/silva-document"
  xmlns:silva="http://infrae.com/namespace/silva"
  xmlns:silva-content="http://infrae.com/namespace/metadata/silva-content"
  xmlns:silva-extra="http://infrae.com/namespace/metadata/silva-extra"
  version="1.0">

  <xsl:import href="silvabase:doc_elements.xslt"/>

  <xsl:output
    method="xml"
    omit-xml-declaration="yes"
    indent="yes"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
    doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" />

  <xsl:template match="/">
    <div class="newsitem">
      <xsl:apply-templates />
    </div>
  </xsl:template>

  <xsl:template match="doc:doc">
    <div class="newsitemcontent">
      <xsl:apply-templates />
    </div>
  </xsl:template>

  <xsl:template match="silva:metadata">
    <h2 class="heading newsitemheading">
      <xsl:value-of select="silva:set[@id='silva-content']/silva-content:maintitle" />
    </h2>
    <div class="newsiteminfo">
      <p class="p publicationdate">
        Publication date:
        <span class="datetime">
          <xsl:value-of select="../../silva:workflow/silva:version/silva:publication_datetime"/>
        </span>
      </p>
    </div>
  </xsl:template>

  <xsl:template match="silva:workflow" />

</xsl:stylesheet>
