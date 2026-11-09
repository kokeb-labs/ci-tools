// Seeded violation: an overrider marked only with virtual, not with override or final.
#include <cstdint>

namespace kv::rule_13_3_1::bad {

class Port {
 public:
  virtual ~Port() = default;
  virtual std::int32_t read() const = 0;
};

class Fake : public Port {
 public:
  virtual std::int32_t read() const { return 1; }
};

std::int32_t sample(const Port& p) { return p.read(); }

}  // namespace kv::rule_13_3_1::bad
