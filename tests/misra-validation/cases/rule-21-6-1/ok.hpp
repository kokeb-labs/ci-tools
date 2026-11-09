// Compliant: fixed storage with automatic duration; nothing is allocated.
#ifndef KV_RULE_21_6_1_OK_HPP
#define KV_RULE_21_6_1_OK_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_21_6_1::ok {

[[nodiscard]] inline std::array<std::int32_t, 4U> make_counters() { return {}; }

[[nodiscard]] inline std::size_t capacity() { return make_counters().size(); }

}  // namespace kv::rule_21_6_1::ok

#endif  // KV_RULE_21_6_1_OK_HPP
