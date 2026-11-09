// Seeded violations (specifiers): an overriding destructor declared with no specifier, override together with
// final, and virtual together with final on a function that overrides nothing.
#include <cstdint>

namespace kv::rule_13_3_1::bad_specifiers {

class Port {
 public:
  virtual ~Port() = default;
  virtual std::int32_t read() const = 0;
  virtual std::int32_t width() const final { return 8; }  // seeded
};

class Fake : public Port {
 public:
  ~Fake() {}                                              // seeded
  std::int32_t read() const override final { return 1; }  // seeded
};

std::int32_t sample(const Port& p) { return p.read() + p.width(); }

}  // namespace kv::rule_13_3_1::bad_specifiers
