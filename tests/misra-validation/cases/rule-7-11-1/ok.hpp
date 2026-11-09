#ifndef KV_RULE_7_11_1_OK_HPP
#define KV_RULE_7_11_1_OK_HPP

// Compliant: the null pointer is always nullptr.
#include <cstdint>

namespace kv::rule_7_11_1::ok {

inline bool missing(std::int32_t const* p) { return p == nullptr; }

}  // namespace kv::rule_7_11_1::ok

#endif  // KV_RULE_7_11_1_OK_HPP
