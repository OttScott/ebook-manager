# Calibre Import Investigation: "Add in Place" Options

## Question Investigated

Can Calibre be configured to import books without copying files (e.g., using symlinks, hardlinks, or "add in place")?

## Findings

### Official Documentation Review

After reviewing the comprehensive Calibre documentation, including:

- `calibredb` command-line manual
- Calibre FAQ
- Library management principles

### Conclusion: **NO**

**Calibre does NOT support importing books without copying them.**

### Key Evidence

1. **No command-line options**: The `calibredb add` command has no options for:
   - `--symlink` or `--link`
   - `--no-copy` or `--add-in-place`
   - `--hardlink` or similar

2. **Deliberate design philosophy**: From the Calibre FAQ:
   > "By managing books in its own folder structure of Author -> Title -> Book files, calibre is able to achieve a high level of reliability and standardization."

3. **Explicit policy**: The FAQ explicitly states:
   > "Kindly do not contact us in an attempt to get us to change this."

### Technical Behavior

When Calibre imports a book:

1. **Always copies files** into its managed library structure
2. **Renames files** according to its preferences (`Author/Title/filename.ext`)
3. **Completely loses the original file path**
4. **Uses internal ID numbers** for database integrity

### Why This Matters for ebook-manager

This behavior explains why:

- **Path-based sync failed**: After Calibre import, original file paths no longer exist in Calibre
- **Metadata-based sync was necessary**: The only way to match books is by title/author metadata
- **Files are duplicated**: Each imported book creates a copy in Calibre's library folder

## Impact on Integration

### What Works

✅ **Metadata-based sync**: Our `sync-calibre` command successfully matches books by title/author  
✅ **Import workflow**: Books can be imported to Calibre via `calibre-import` and `dual-import`  
✅ **After-move sync**: Calibre database can be updated when beets moves files  

### Limitations

❌ **No space savings**: Calibre imports always duplicate files  
❌ **No "live sync"**: Changes to original files don't affect Calibre copies  
❌ **Storage overhead**: Users need space for both beets and Calibre copies  

## Recommendations

### For Users

1. **Accept file duplication**: This is Calibre's intended behavior
2. **Use sync judiciously**: Only import books you actually want in Calibre
3. **Consider storage needs**: Plan for ~2x storage requirements
4. **Use metadata-based sync**: Our sync logic handles the path mismatch correctly

### For Development

1. **Current implementation is optimal**: Metadata-based matching is the only viable approach
2. **Document the limitation**: Users should understand that Calibre will duplicate files
3. **Consider selective import**: Maybe add options to filter which books get imported to Calibre

## Alternative Solutions Considered

### Possible Workarounds

1. **Calibre plugins**: Could theoretically modify import behavior, but:
   - Would require custom plugin development
   - Would fight against Calibre's core design
   - Likely to break with updates

2. **External tools**: Could maintain symlinks manually, but:
   - Fragile and error-prone  
   - Would confuse Calibre's database
   - Not sustainable

### Conclusion

**No viable workarounds exist.** Calibre's architecture fundamentally requires file copying.

## Final Assessment

The metadata-based sync approach implemented in ebook-manager v2.0 is the **optimal solution** given Calibre's constraints. File duplication is an unavoidable cost of Calibre integration.

---
*Investigation completed: December 2024*  
*Status: RESOLVED - No technical solution available*
