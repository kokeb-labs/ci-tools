// Compliant: a raw string, where the backslash is not an escape.
#ifndef KV_RULE_5_13_1_RAW_STRING_OK_HPP
#define KV_RULE_5_13_1_RAW_STRING_OK_HPP


namespace kv::rule_5_13_1_raw_string::ok {

inline const char* raw() { return R"(dir\qfile)"; }

}  // namespace kv::rule_5_13_1_raw_string::ok

#endif  // KV_RULE_5_13_1_RAW_STRING_OK_HPP
