<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:t="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="t">

  <!-- this all comes from https://github.com/PerseusDL/perseus_nemo_ui/tree/master/perseus_nemo_ui/data/assets/static/xslt -->

  <xsl:output xml:space="default" method="html"/>

  <!-- glyphs -->
  <!-- <xsl:include href="teig.xsl" /> -->
  <xsl:template match="//g">
    <xsl:choose>
      <xsl:when test="@type='crux' or @type='cross'">
        <xsl:text>†</xsl:text>
      </xsl:when>
      <xsl:when test="@type='crosses'">
        <xsl:text>††</xsl:text>
      </xsl:when>
      <xsl:when test="@type='drachma'">
        <xsl:text>₯</xsl:text>
      </xsl:when>
      <xsl:when test="@type='year'">
        <xsl:text>L</xsl:text>
      </xsl:when>
      <xsl:when test="@type='stop'">
        <xsl:text>•</xsl:text>
      </xsl:when>
      <xsl:when test="@type = 'stauros'">
        <xsl:text>+</xsl:text>
      </xsl:when>
      <xsl:when test="@type = 'staurogram'">
        <xsl:text>⳨</xsl:text>
      </xsl:when>
      <xsl:when test="@type = 'leaf'">
        <xsl:text>❦</xsl:text>
      </xsl:when>
      <xsl:when test="@type = 'dipunct'">
        <xsl:text>:</xsl:text>
      </xsl:when>
      <xsl:when test="@type='apostrophe'">
        <xsl:text>’</xsl:text>
      </xsl:when>
      <xsl:when test="@type='check' or @type='check-mark'">
        <xsl:text>／</xsl:text>
      </xsl:when>
      <xsl:when test="@type='chirho'">
        <xsl:text>☧</xsl:text>
      </xsl:when>
      <xsl:when test="@type='dash'">
        <xsl:text>—</xsl:text>
      </xsl:when>
      <xsl:when test="@type='dipunct'">
        <xsl:text>∶</xsl:text>
      </xsl:when>
      <xsl:when test="@type='filled-circle'">
        <xsl:text>⦿</xsl:text>
      </xsl:when>
      <xsl:when test="@type='filler' and @rend='extension'">
        <xsl:text>―</xsl:text>
      </xsl:when>
      <xsl:when test="@type='latin-interpunct' or @type='middot' or @type='mid-punctus'">
        <xsl:text>·</xsl:text>
      </xsl:when>
      <xsl:when test="@type='monogram'">
        <span class="italic">
          <xsl:text>monogr.</xsl:text>
        </span>
      </xsl:when>
      <xsl:when test="@type='upper-brace-opening'">
        <xsl:text>⎧</xsl:text>
      </xsl:when>
      <xsl:when test="@type='center-brace-opening'">
        <xsl:text>⎨</xsl:text>
      </xsl:when>
      <xsl:when test="@type='lower-brace-opening'">
        <xsl:text>⎩</xsl:text>
      </xsl:when>
      <xsl:when test="@type='upper-brace-closing'">
        <xsl:text>⎫</xsl:text>
      </xsl:when>
      <xsl:when test="@type='center-brace-closing'">
        <xsl:text>⎬</xsl:text>
      </xsl:when>
      <xsl:when test="@type='lower-brace-closing'">
        <xsl:text>⎭</xsl:text>
      </xsl:when>
      <xsl:when test="@type='parens-upper-opening'">
        <xsl:text>⎛</xsl:text>
      </xsl:when>
      <xsl:when test="@type='parens-middle-opening'">
        <xsl:text>⎜</xsl:text>
      </xsl:when>
      <xsl:when test="@type='parens-lower-opening'">
        <xsl:text>⎝</xsl:text>
      </xsl:when>
      <xsl:when test="@type='parens-upper-closing'">
        <xsl:text>⎞</xsl:text>
      </xsl:when>
      <xsl:when test="@type='parens-middle-closing'">
        <xsl:text>⎟</xsl:text>
      </xsl:when>
      <xsl:when test="@type='parens-lower-closing'">
        <xsl:text>⎠</xsl:text>
      </xsl:when>
      <xsl:when test="@type = 'rho-cross'">
        <xsl:text>⳨</xsl:text>
      </xsl:when>
      <xsl:when test="@type='slanting-stroke'">
        <xsl:text>/</xsl:text>
      </xsl:when>
      <xsl:when test="@type='stauros'">
        <xsl:text>†</xsl:text>
      </xsl:when>
      <xsl:when test="@type='tachygraphic marks'">
        <span class="italic">
          <xsl:text>tachygr. marks</xsl:text>
        </span>
      </xsl:when>
      <xsl:when test="@type='tripunct'">
        <xsl:text>⋮</xsl:text>
      </xsl:when>
      <xsl:when test="@type='double-vertical-bar'">
        <xsl:text>‖</xsl:text>
      </xsl:when>
      <xsl:when test="@type='long-vertical-bar'">
        <xsl:text>|</xsl:text>
      </xsl:when>
      <xsl:when test="@type='x'">
        <xsl:text>☓</xsl:text>
      </xsl:when>
      <xsl:when test="@type='xs'">
        <xsl:text>☓</xsl:text>
        <xsl:text>☓</xsl:text>
        <xsl:text>☓</xsl:text>
        <xsl:text>☓</xsl:text>
        <xsl:text>☓</xsl:text>
      </xsl:when>
      <xsl:when test="@type='milliaria'">
        <xsl:text>ↀ</xsl:text>
      </xsl:when>
      <xsl:when test="@type='leaf'">
        <xsl:text>❦</xsl:text>
      </xsl:when>
      <xsl:when test="@type='palm'">
        <xsl:text>††</xsl:text>
      </xsl:when>
      <xsl:when test="@type='star'">
        <xsl:text>*</xsl:text>
      </xsl:when>
      <xsl:when test="@type='interpunct'">
        <xsl:text>·</xsl:text>
      </xsl:when>
      <xsl:when test="@type='sestertius'">
        <xsl:text>𐆘</xsl:text>
      </xsl:when>
      <xsl:when test="@type='denarius'">
        <xsl:text>𐆖</xsl:text>
      </xsl:when>
      <xsl:when test="@type='barless-A'">
        <xsl:text>Λ</xsl:text>
      </xsl:when>
      <xsl:when test="@type='dot'">
        <xsl:text>.</xsl:text>
      </xsl:when>
      <xsl:when test="@type='stop'">
        <xsl:text>•</xsl:text>
      </xsl:when>
      <xsl:when test="@type='crux' or @type='cross'">
        <xsl:text>†</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <span class="smaller" style="font-style:italic;">
          <xsl:text>(symbol: </xsl:text>
          <xsl:value-of select="@type"/>
          <xsl:text>)</xsl:text>
        </span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <!-- edition -->

  <!-- <xsl:include href="edition.xsl" />   -->
  <xsl:template match="t:div[@type = 'edition']">
    <div id="edition">
      <xsl:attribute name="class">
        <xsl:text>edition lang_</xsl:text>
        <xsl:value-of select="@xml:lang"/>
      </xsl:attribute>
      <xsl:choose>
          <xsl:when test="child::t:l">
              <ol><xsl:apply-templates /></ol>
          </xsl:when>
          <xsl:otherwise>
              <xsl:apply-templates/>
          </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <xsl:template match="t:div[@type = 'textpart']">
    <xsl:element name="div">
      <xsl:attribute name="class">textpart <xsl:value-of select="@subtype" /></xsl:attribute>
      <xsl:if test="@n">
        <xsl:attribute name="data-n">
          <xsl:value-of select="@n" />
        </xsl:attribute>
        <xsl:element name="div">
          <xsl:attribute name="class">a</xsl:attribute>
          <xsl:attribute name="data-ref">
            <xsl:for-each select="ancestor::t:div[@type='textpart']/@n">
              <xsl:value-of select="concat(., '.')" />
            </xsl:for-each>
            <xsl:value-of select="@n" />
          </xsl:attribute>
          <xsl:if test="@n">
            <div>
              <xsl:value-of select="@n" />
            </div>
          </xsl:if>
        </xsl:element>
      </xsl:if>
      <div class="b">
        <xsl:choose>
          <xsl:when test="child::t:l">
            <ol><xsl:apply-templates /></ol>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates/>
          </xsl:otherwise>
        </xsl:choose>
      </div>
    </xsl:element>
  </xsl:template>

  <xsl:template match="t:w">
    <xsl:element name="span">
      <xsl:attribute name="class">w</xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="t:quote">
    <xsl:element name="blockquote">
      <xsl:choose>
        <xsl:when test="child::t:l">
            <ol class="hidenum"><xsl:apply-templates /></ol>
        </xsl:when>
        <xsl:otherwise>
            <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

  <xsl:template match="t:figure" />

  <xsl:template match="t:l">
    <xsl:element name="li">
      <xsl:attribute name="value"><xsl:value-of select="@n"/></xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="t:seg">
    <xsl:element name="span">
      <xsl:attribute name="class">seg</xsl:attribute>
      <xsl:attribute name="value"><xsl:value-of select="@n"/></xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="t:pb">
    <div class='pb'><xsl:value-of select="@n"/></div>
  </xsl:template>

  <xsl:template match="t:ab/text()">
    <xsl:value-of select="." />
  </xsl:template>

  <xsl:template match="t:p">
    <p>
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <xsl:template match="t:name/t:reg"></xsl:template>
  <xsl:template match="t:name/t:placeName"><span class="placeName"><xsl:apply-templates/></span></xsl:template>

  <xsl:template match="t:lb">
    <br/>
  </xsl:template>

  <xsl:template match="t:ex">
  	<span class="ex">
    	<xsl:text>(</xsl:text><xsl:value-of select="." /><xsl:text>)</xsl:text>
    </span>
  </xsl:template>

  <xsl:template match="t:abbr">
  	<span class="abbr">
    	<xsl:text></xsl:text><xsl:value-of select="." /><xsl:text></xsl:text>
    </span>
  </xsl:template>

  <xsl:template match="t:gap">
    <span class="gap">
      <xsl:choose>
        <xsl:when test="@quantity and @unit='character'">
          <xsl:value-of select="string(@quantity)" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>---</xsl:text>
        </xsl:otherwise>
      </xsl:choose>

    </span>
  </xsl:template>

  <xsl:template match="t:head">
    <div class="head">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="t:sp">
    <div class="speak">
      <xsl:if test="./t:speaker">
        <em><xsl:value-of select="./t:speaker/text()" /></em>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="./t:l">
          <ol>
            <xsl:apply-templates select="./t:l"/>
          </ol>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <xsl:template match="t:supplied">
    <span>
      <xsl:attribute name="class">supplied supplied_<xsl:value-of select='@cert' /></xsl:attribute>
      <xsl:text>[</xsl:text>
      <xsl:apply-templates/><xsl:if test="@cert = 'low'"><xsl:text>?</xsl:text></xsl:if>
      <xsl:text>]</xsl:text>
    </span>
  </xsl:template>

  <xsl:template match="t:note">
    <span class="note"><a href="#">[*]</a><span class="note-content"><xsl:text>(</xsl:text><xsl:value-of select="." /><xsl:text>)</xsl:text></span></span>
  </xsl:template>

  <xsl:template match="t:choice">
    <span class="choice">
      <xsl:attribute name="title">
        <xsl:value-of select="reg" />
      </xsl:attribute>
      <xsl:value-of select="orig" /><xsl:text> </xsl:text>
    </span>
  </xsl:template>

  <xsl:template match="t:unclear">
    <span class="unclear"><xsl:value-of select="." /></span>
  </xsl:template>

  <!-- <xsl:include href="translation.xsl" /> -->

  <xsl:template match="//t:div[@type = 'translation']">
    <div>
      <xsl:attribute name="id">
        <xsl:text>translation</xsl:text>
        <xsl:if test="@xml:lang"><xsl:text>_</xsl:text></xsl:if>
        <xsl:value-of select="@xml:lang"/>
      </xsl:attribute>

      <xsl:attribute name="class">
        <xsl:text>translation lang_</xsl:text>
        <xsl:value-of select="@xml:lang"/>
      </xsl:attribute>

      <xsl:apply-templates/>

    </div>
  </xsl:template>

  <!-- others: just remove for now -->

  <!-- <xsl:include href="teiHeader.xsl" /> -->
  <xsl:template match="//t:teiHeader" />

  <!-- <xsl:include href="facsimile.xsl" /> -->
  <xsl:template match="//t:facsimile" />

  <!-- <xsl:include href="text.xsl" /> -->
  <xsl:template match="t:div[not(@type = 'edition') and not(@type = 'translation') and not(@type= 'textpart')]" />

</xsl:stylesheet>
