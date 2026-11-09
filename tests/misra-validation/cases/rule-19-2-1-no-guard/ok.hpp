#ifndef KV_RULE_19_2_1_NO_GUARD_OK_HPP
#define KV_RULE_19_2_1_NO_GUARD_OK_HPP

// Compliant: the whole header sits inside an include guard.
#include <cstdint>

namespace kv::rule_19_2_1_no_guard::ok {

inline std::uint8_t one() { return 1U; }

}  // namespace kv::rule_19_2_1_no_guard::ok

#endif  // KV_RULE_19_2_1_NO_GUARD_OK_HPP
