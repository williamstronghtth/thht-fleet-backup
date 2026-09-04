# Property Lookup Automation Tool - Technical Requirements

**Author:** Jack Sullivan  
**Date:** 2026-02-19  
**For:** Ryan Chen  
**Status:** Draft

---

## Overview

Build an automated tool to batch-search property ownership records against the Volusia County Property Appraiser database, matching a list of names to their associated properties.

---

## Requirements

### 1. Input Specification

- **Format:** CSV file
- **Structure:** Two columns
  - Column 1: `Last Name`
  - Column 2: `First Name`
- **Example:**
  ```csv
  Last Name,First Name
  Smith,John
  Johnson,Mary
  Williams,Robert
  ```

### 2. Processing

- **Target:** Volusia County Property Appraiser
  - **URL:** `https://vcpa.vcgov.org/search/real-property-classic`
  - **Search Field:** Owner Name
  
- **Search Logic:**
  - Concatenate as "Last Name, First Name" for Owner Name search
  - Handle partial matches (e.g., "SMITH, JOHN" should match "SMITH, JOHN A" or "SMITH, JOHN & MARY")
  - Capture ALL properties associated with each name (one person may own multiple parcels)

- **Rate Limiting:**
  - Implement delays between requests (suggested: 1-2 seconds minimum)
  - Respect `robots.txt` if present
  - Consider exponential backoff on errors/timeouts
  - Target: No more than 30 requests per minute

### 3. Output Specification

- **Format:** CSV file
- **Columns:**
  | Column | Description |
  |--------|-------------|
  | `Original Name` | The input name as provided (Last, First) |
  | `Matched Owner Name` | The owner name as it appears in VCPA records |
  | `Property Address` | Street address of the property |
  | `City` | City/municipality |
  | `Parcel ID` | Unique parcel identifier |
  | `Property Class` | Property classification (e.g., Single Family, Vacant, Commercial) |

- **Example Output:**
  ```csv
  Original Name,Matched Owner Name,Property Address,City,Parcel ID,Property Class
  Smith, John,SMITH JOHN A,123 MAIN ST,DAYTONA BEACH,1234-56-78-9012,Single Family
  Smith, John,SMITH JOHN A,456 OAK AVE,DAYTONA BEACH,1234-56-78-9013,Vacant
  Johnson, Mary,JOHNSON MARY L,789 PINE RD,ORMOND BEACH,2345-67-89-0123,Single Family
  Williams, Robert,NO MATCH FOUND,,,, 
  ```

### 4. Edge Cases & Error Handling

- **No matches found:** Include row with "NO MATCH FOUND" in Matched Owner Name, empty remaining fields
- **Multiple matches:** Create separate row for each property
- **Timeout/errors:** Log and retry with backoff, or mark as "ERROR - RETRY"
- **Special characters:** Handle apostrophes, hyphens in names (e.g., O'Brien, Smith-Jones)

---

## Technical Notes

### Website Interaction

The VCPA classic search interface may require:
- Form submission (POST request) or URL parameter construction
- Session handling / cookies
- Parsing HTML response tables

### Recommended Approach

1. **Scraping:** Use Python with `requests` + `BeautifulSoup` or `Playwright`/`Selenium` if JavaScript rendering required
2. **Async:** Consider `asyncio` with rate limiting for better performance on large lists
3. **Logging:** Comprehensive logging for debugging and audit trail
4. **Checkpointing:** Save progress periodically for large batches (resume on failure)

---

## Success Criteria

- [ ] Processes CSV input without manual intervention
- [ ] Correctly matches names to property records
- [ ] Handles multiple properties per owner
- [ ] Respects rate limits (no site blocking)
- [ ] Produces clean CSV output ready for further analysis
- [ ] Logs errors and edge cases for review

---

## Questions for Ryan

1. Expected batch sizes? (10s, 100s, 1000s of names?)
2. Preferred language/framework?
3. Any existing VCPA scraping experience or known gotchas?
4. Timeline/priority?

---

*Contact: jack@thehooverhometeam.com*
