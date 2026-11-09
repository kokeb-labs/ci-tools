// Near miss: every enumerator keeps its default value, so the guideline's exception waives the fixed type.
#ifndef KV_RULE_10_2_1_OK_DEFAULT_HPP
#define KV_RULE_10_2_1_OK_DEFAULT_HPP

namespace kv::rule_10_2_1::ok_default {

enum class Mode { kIdle, kRun };

[[nodiscard]] inline bool running(Mode m) { return m == Mode::kRun; }

}  // namespace kv::rule_10_2_1::ok_default

#endif  // KV_RULE_10_2_1_OK_DEFAULT_HPP
