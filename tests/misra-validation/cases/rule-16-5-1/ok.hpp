#ifndef KV_RULE_16_5_1_OK_HPP
#define KV_RULE_16_5_1_OK_HPP

// Compliant: named functions instead of overloaded logical operators.
namespace kv::rule_16_5_1::ok {

struct Flag {
  bool set = false;
};

[[nodiscard]] inline bool both(Flag a, Flag b) { return a.set && b.set; }
[[nodiscard]] inline bool either(Flag a, Flag b) { return a.set || b.set; }

}  // namespace kv::rule_16_5_1::ok

#endif  // KV_RULE_16_5_1_OK_HPP
