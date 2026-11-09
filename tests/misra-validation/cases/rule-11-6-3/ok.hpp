// Compliant: every enumerator value is distinct.
#ifndef KV_RULE_11_6_3_OK_HPP
#define KV_RULE_11_6_3_OK_HPP

#include <cstdint>

namespace kv::rule_11_6_3::ok {

enum class Code : std::uint8_t { kA = 1, kB, kC = 3 };

inline bool is_b(Code x) { return x == Code::kB; }

}  // namespace kv::rule_11_6_3::ok

#endif  // KV_RULE_11_6_3_OK_HPP
