// Compliant: conditions of type bool, or of a class with an explicit operator bool (exception 2),
// written in a class template whose port type is a template parameter.
#ifndef KV_RULE_7_0_2_OK_TEMPLATE_HPP
#define KV_RULE_7_0_2_OK_TEMPLATE_HPP

#include <cstdint>

namespace kv::rule_7_0_2::ok_template {

struct Result {
  std::int32_t error{0};
  [[nodiscard]] constexpr bool ok() const noexcept { return error == 0; }
  constexpr explicit operator bool() const noexcept { return ok(); }
};

template <typename Port>
class Driver {
 public:
  explicit Driver(Port& port) noexcept : port_{port} {}

  Result Start() noexcept {
    if (auto r = step(); !r) {  // ! on a class with explicit operator bool
      return r;
    }
    if (!port_.Ready()) {  // a bool hook of the dependent port
      return Result{1};
    }
    const auto r = step();
    return r ? Result{0} : r;  // class with explicit operator bool as the ?: condition
  }

 private:
  Result step() noexcept { return Result{0}; }
  Port& port_;
};

struct FakePort {
  bool Ready() noexcept { return true; }
};

inline bool run() noexcept {
  FakePort port{};
  Driver<FakePort> driver{port};
  return driver.Start().ok();
}

}  // namespace kv::rule_7_0_2::ok_template

#endif  // KV_RULE_7_0_2_OK_TEMPLATE_HPP
