// Compliant: a fixed array of bool passed by reference to const.
#ifndef KV_RULE_26_3_1_CONST_OK_HPP
#define KV_RULE_26_3_1_CONST_OK_HPP

#include <array>
#include <cstddef>

namespace kv::rule_26_3_1_const::ok {

[[nodiscard]] inline std::size_t count_flags(const std::array<bool, 4U>& flags) { return flags.size(); }

}  // namespace kv::rule_26_3_1_const::ok

#endif  // KV_RULE_26_3_1_CONST_OK_HPP
