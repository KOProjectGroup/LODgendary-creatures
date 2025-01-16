<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output method="html" indent="yes" />

    <xsl:template match="/">
        <html>
            <head>
                <title><xsl:value-of select="//tei:title" /></title>
            </head>
            <body>
                <div class="container">
                    <section class="header">
                        <h1><xsl:value-of select="//tei:title" /></h1>
                        <h2>By <xsl:value-of select="//tei:author" /></h2>
                        <h3>Published by <xsl:value-of select="//tei:publisher" />, <xsl:value-of select="//tei:pubPlace" /> in <xsl:value-of select="//tei:date" /></h3>
                        <div class="source">
                            <h4>Source Details</h4>
                            <ul>
                                <li><strong>Title</strong>: <xsl:value-of select="//tei:sourceDesc/tei:bibl/tei:title" /></li>
                                <li><strong>Author</strong>: <xsl:value-of select="//tei:sourceDesc/tei:bibl/tei:author" /></li>
                                <li><strong>Editor</strong>: <xsl:value-of select="//tei:sourceDesc/tei:bibl/tei:editor" /></li>
                                <li><strong>Publisher</strong>: <xsl:value-of select="//tei:sourceDesc/tei:bibl/tei:publisher" /></li>
                                <li><strong>Publication Place</strong>: <xsl:value-of select="//tei:sourceDesc/tei:bibl/tei:pubPlace" /></li>
                                <li><strong>Publication Date</strong>: <xsl:value-of select="//tei:sourceDesc/tei:bibl/tei:date" /></li>
                                <li><strong>ISBN</strong>: <xsl:value-of select="//tei:sourceDesc/tei:bibl/tei:idno[@type='ISBN']" /></li>
                            </ul>
                        </div>
                    </section>
                    <section class="people">
                        <div>
                            <h4>People Mentioned</h4>
                            <ul>
                                <xsl:for-each select="//tei:listPerson/tei:person">
                                    <li>
                                        <xsl:value-of select="tei:persName[@xml:lang='en']" />
                                        <xsl:if test="tei:persName[@xml:lang='it']"> (<xsl:value-of select="tei:persName[@xml:lang='it']" />)
                                        </xsl:if>
                                        <xsl:if test="tei:birth"> - Born in <xsl:value-of select="tei:birth/@when" />
                                        </xsl:if>
                                        <xsl:if test="tei:death">, Died in <xsl:value-of select="tei:death/@when" />
                                        </xsl:if>
                                    </li>
                                </xsl:for-each>
                            </ul>
                        </div>
                    </section>
                    <section class="content">
                        <div>
                            <h4>Content</h4>
                            <xsl:apply-templates select="//tei:body" />
                        </div>
                    </section>
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="tei:body">
        <div>
            <xsl:apply-templates select="*" />
        </div>
    </xsl:template>

    <xsl:template match="tei:head">
        <xsl:choose>
            <xsl:when test="@rend">
                <xsl:variable name="rend" select="@rend"/>
                <xsl:variable name="style">
                    <xsl:text></xsl:text>
                    <xsl:if test="contains($rend, 'align(center)')">
                        <xsl:text>text-align: center;</xsl:text>
                    </xsl:if>
                    <xsl:if test="contains($rend, 'italic')">
                        <xsl:text> font-style: italic;</xsl:text>
                    </xsl:if>
                    <xsl:if test="contains($rend, 'case(allcaps)')">
                        <xsl:text> text-transform: uppercase;</xsl:text>
                    </xsl:if>
                </xsl:variable>
                <h2>
                    <xsl:attribute name="style">
                        <xsl:value-of select="$style"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </h2>
            </xsl:when>
            <xsl:otherwise>
                <h2>
                    <xsl:apply-templates/>
                </h2>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="tei:p">
        <p><xsl:apply-templates select="node()" /></p>
    </xsl:template>

    <xsl:template match="tei:persName">
        <span class="person"><xsl:value-of select="." /></span>
    </xsl:template>

    <xsl:template match="tei:foreign">
        <i>
            <xsl:attribute name="title">
                lang: <xsl:value-of select="@xml:lang" />
            </xsl:attribute>
            <xsl:value-of select="." />
        </i>
    </xsl:template>


    <xsl:template match="tei:note">
        <sup><xsl:value-of select="@n" /></sup>
    </xsl:template>

    <xsl:template match="tei:placeName">
        <a href="{@ref}"><xsl:value-of select="." /></a>
    </xsl:template>

    <xsl:template match="tei:figure">
        <figure>
            <img src="{tei:graphic/@url}" alt="{tei:head[1]}" />
            <figcaption>
                <span>
                    <xsl:value-of select="tei:head[1]" />
                </span>
                <span>
                    (<xsl:value-of select="tei:head[2]" />)
                </span>
            </figcaption>
        </figure>
    </xsl:template>

</xsl:stylesheet>