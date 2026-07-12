# Alibaba Java Coding Guidelines Summary

Source: Alibaba Java Coding Guidelines official page.

This file is a concise operational summary for agents. It does not replace the official document.

## Severity

- Mandatory: treat violations as defects.
- Recommended: follow by default unless the project has a clear reason not to.
- Reference: use as design guidance.

## 1. Programming Specification

### Naming

- Do not start or end names with an underscore or dollar sign.
- Avoid Chinese, Pinyin, or mixed Pinyin-English naming. Proper nouns such as Alibaba, Taobao, Youku, and Hangzhou are acceptable.
- Use UpperCamelCase for classes. Domain model suffixes such as DO, BO, DTO, and VO stay uppercase.
- Use lowerCamelCase for methods, parameters, fields, and local variables.
- Use uppercase words separated by underscores for constants.
- Abstract classes should start with `Abstract` or `Base`; exception classes should end with `Exception`; tests should start with the tested class name and end with `Test`.
- Use `String[] args`, not `String args[]`.
- Boolean fields should not start with `is` when framework serialization may infer a different property name.
- Package names are lowercase and usually singular.
- Avoid unclear abbreviations. Design pattern names may be included in class names, such as `OrderFactory`.
- Service and DAO types should usually be interfaces, with implementations ending in `Impl`.
- Enum class names should end with `Enum`; enum members use uppercase words separated by underscores.

### Constants and Formatting

- Do not use magic values.
- Use uppercase `L` for long literals.
- Group constants by function instead of creating one oversized constants class.
- Prefer enums for fixed value sets.
- Use 4 spaces for indentation.
- Keep lines within 120 characters when practical.
- Use UTF-8 and Unix line endings.
- Keep operators surrounded by spaces.

### Object-Oriented Code

- Access static fields and methods through the class name.
- Mark methods that reimplement interface or abstract class methods with Java's standard compiler annotation.
- Use varargs only for same-type, same-meaning parameters and keep them last.
- Mark deprecated APIs with `@Deprecated` and document alternatives.
- Prefer calling `equals` on known non-null values.
- Compare floating point values with a tolerance or `BigDecimal`, not direct equality.
- Use wrapper types for POJO fields and RPC parameters or results; local variables may use primitives.
- Do not set default values in DO, DTO, or VO fields unless the project explicitly requires it.
- Avoid business logic in constructors.
- Implement useful `toString` methods for POJOs.

### Collections, Concurrency, and Control Flow

- Redefine `hashCode` whenever `equals` is redefined.
- Understand that `subList` is a view of the original list.
- `Arrays.asList` returns a fixed-size list.
- Do not modify a collection inside a foreach loop; use an iterator for removal.
- Specify expected collection capacity when practical.
- Prefer `entrySet` when iterating over map keys and values.
- Use thread pools instead of repeatedly creating raw threads.
- Name threads and thread pools clearly.
- Configure thread pool parameters for the business scenario.
- Avoid sharing non-thread-safe objects such as `SimpleDateFormat`.
- Every `switch` case should end with `break`, `return`, or a comment explaining intentional fall-through.
- Prefer guard clauses to deep nesting.
- Extract complex boolean expressions into named variables or methods.

### Comments

- Use Javadoc for classes, fields, and public methods.
- Document abstract methods, interface methods, complex business logic, special branches, algorithms, and boundary values.
- Keep comments synchronized with code.

## 2. Exceptions and Logging

### Exceptions

- Do not catch runtime exceptions such as `NullPointerException` as a substitute for validation.
- Do not use exceptions for normal control flow.
- Keep try-catch scopes small.
- Do not swallow exceptions.
- Make transaction rollback behavior explicit.
- Close resources with try-with-resources or equivalent cleanup.
- Do not return or throw new exceptions from `finally`.
- Avoid throwing broad `RuntimeException`, `Exception`, or `Throwable`; use meaningful business exceptions.
- Document nullable returns.

### Logging

- Use a logging facade such as SLF4J.
- Use placeholders or log-level checks for debug and trace messages.
- Include both context and stack trace in exception logs.
- Separate business logs from error logs when useful.
- Avoid logging sensitive data such as passwords, keys, full phone numbers, and personal identifiers.

## 3. MySQL Rules

### Schema

- Boolean-like columns use `is_xxx` and unsigned tinyint, while Java POJO fields avoid the `is` prefix and map explicitly.
- Table and column names use lowercase letters, digits, and underscores.
- Do not use plural table names.
- Do not use MySQL reserved words.
- Name primary indexes with `pk_`, unique indexes with `uk_`, and normal indexes with `idx_`.
- Use `decimal` for precise numeric values instead of `float` or `double`.
- Size `varchar` fields based on real business needs.
- Tables should include `gmt_create` and `gmt_modified`.

### Indexes and SQL

- Fields that are unique by business rule must have unique indexes.
- Avoid joins involving more than three tables.
- Joined columns must have compatible data types and indexes.
- Specify index length for indexed varchar columns.
- Avoid `LIKE '%xxx'` and `LIKE '%xxx%'` in paginated searches.
- Prefer covering indexes and index-friendly `ORDER BY` clauses.
- Optimize large offset pagination.
- Use `COUNT(*)` for row counts.
- Use `IS NULL` or `ISNULL()` for null checks.
- Query count before paginated data retrieval when that is part of the flow.
- Avoid foreign keys, cascades, and stored procedures in application schemas when following this guideline.
- Confirm target rows before data correction, deletion, or update operations.

### ORM

- Select explicit columns instead of `SELECT *`.
- Use MyBatis `#{}` for parameters. Do not use `${}` with user input.
- Do not use `HashMap` or `Hashtable` as database result models.
- Update `gmt_modified` when records change.
- Avoid generic "update anything" APIs; update explicit fields.
- Use transactions with careful scope and rollback semantics.

## 4. Project Specification

- Keep layering clear: web, service, manager, DAO, and external integration code should each have distinct responsibilities.
- Web layers handle access control, parameter validation, and request-specific logic.
- Service layers hold business logic.
- Manager layers wrap third-party services, caching, middleware, and reusable DAO compositions.
- DAO layers only handle data access.
- Query objects should represent query criteria; avoid using maps for complex query parameters.
- Use stable Maven coordinates and versioning.
- Online applications should not depend on SNAPSHOT versions unless there is a clear exception.
- Compare dependency trees when upgrading dependencies.
- Use parent `dependencyManagement` for version governance.

## 5. Security Specification

- User-owned pages and operations must perform authorization checks.
- Sensitive user data must be desensitized before display.
- User input used in SQL must be parameterized or constrained by metadata.
- Validate all user input, including page size, sort fields, redirect targets, deserialization, and regex inputs.
- Escape or filter user data before outputting it to HTML.
- Protect forms and AJAX submissions against CSRF.
- Apply anti-replay, rate limiting, and abuse controls to SMS, email, phone, order, payment, and similar resource use.
- Apply anti-fraud, sensitive-word, and risk-control strategies to user-generated content.
