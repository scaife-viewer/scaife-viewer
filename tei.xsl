<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:cts="http://chs.harvard.edu/xmlns/cts" xmlns:tei="http://www.tei-c.org/ns/1.0">
  <xsl:output method="html" />

  <xsl:template match="tei:TEI">
    <div class="TEI"><xsl:apply-templates /></div>
  </xsl:template>

  <xsl:template match="tei:text">
    <xsl:for-each select="descendant::*/text()">
      <xsl:value-of select="normalize-space(.)"/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:apply-templates select="@*|node()"/>
  </xsl:template>

</xsl:stylesheet>
